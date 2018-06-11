from flask import Blueprint, render_template,flash, request,session,jsonify, url_for, current_app, redirect, abort
from flask_login import login_user, logout_user, login_required, current_user
from flask_uploads import UploadNotAllowed
from fly_bbs import db_utils, forms, models, code_msg
from fly_bbs.extensions import mongo, upload_photos, whoosh_searcher
from bson.objectid import ObjectId
from bson.json_util import dumps
from datetime import datetime
import random
api_view = Blueprint("api", __name__, url_prefix="", template_folder="templates")


def add_message(user, content):
    if user and user['_id'] != current_user.user['_id']:
        # user['unread'] = user.get('unread', 0) + 1
        message = {
            'user_id': user['_id'],
            'content': content,
            'create_at': datetime.utcnow()
        }
        mongo.db.messages.insert_one(message)
        mongo.db.users.update({'_id': user['_id']}, {'$inc': {'unread': 1}})


@api_view.route('/upload/<string:name>')
@api_view.route('/upload', methods=['POST'])
def upload(name=None):
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return jsonify(code_msg.USER_UN_LOGIN)
        file = request.files['smfile']
        if not file:
            return jsonify(code_msg.FILE_EMPTY)
        try:
            filename = upload_photos.save(file)
        except UploadNotAllowed:
            return jsonify(code_msg.UPLOAD_UN_ALLOWED)
        # 因为存储在帖子内容里，所以用个相对路径，方便数据转移
        file_url = '/api/upload/' + filename
        result = models.R(data={'url': file_url}).put('code', 0)
        return jsonify(result)
    if not name:
        abort(404)
    return redirect(upload_photos.url(name))


@api_view.route('/adopt/<ObjectId:comment_id>', methods=['POST'])
@login_required
def post_adopt(comment_id):
    if not comment_id:
        abort(404)
    comment = mongo.db.comments.find_one_or_404({'_id': comment_id})
    post = mongo.db.posts.find_one_or_404({'_id': comment['post_id']})
    if post['user_id'] != current_user.user['_id']:
        jsonify(code_msg.USER_UN_HAD_PERMISSION)
    if post.get('accepted', False):
        jsonify(code_msg.HAD_ACCEPTED_ANSWER)
    mongo.db.comments.update_one({'_id': comment_id}, {'$set': {'is_adopted': True}})

    post['accepted'] = True
    mongo.db.posts.save(post)

    # 如果悬赏金币不为0将金币加给回帖人
    reward = post.get('reward', 0)
    user = mongo.db.users.find_one({'_id': comment['user_id']})
    if reward > 0 and user:
        mongo.db.users.update_one({'_id': comment['user_id']}, {'$inc': {'coin': reward}})
    if user:
        # 给回帖人添加一条通知消息
        add_message(user, render_template('user_message/adopt_message.html', post=post, comment=comment))
    return jsonify(models.R.ok())


@api_view.route('/reply/zan/<ObjectId:comment_id>', methods=['POST'])
@login_required
def reply_zan(comment_id):
    ok = request.values.get('ok')
    user_id = current_user.user['_id']
    res = mongo.db.comments.find_one({'_id': comment_id, 'zan': {'$elemMatch': {'$eq': user_id}}})
    # 默认取消点赞
    action = '$pull'
    count = -1
    if ok == 'false' and not res:
        # 点赞
        action = '$push'
        count = 1
        # 留个坑有空填，点赞通知
    mongo.db.comments.update_one({'_id': comment_id},
                                 {action: {'zan': user_id}, '$inc': {'zan_count': count}})
    return jsonify(models.R().ok())


@api_view.route('/reply', methods=['POST'])
@login_required
def post_reply():
    post_id = request.values.get('id')
    if not post_id:
        abort(404)
    post_id = ObjectId(post_id)
    post = mongo.db.posts.find_one_or_404({'_id': post_id})
    user = current_user.user
    content = request.values.get('content')
    if not user.get('is_active', False) or user.get('is_disabled', False):
        return jsonify(code_msg.USER_UN_ACTIVE_OR_DISABLED)
    if not content:
        return jsonify(code_msg.POST_CONTENT_EMPTY)

    comment = {
        'content': content,
        'post_id': post_id,
        'user_id': user['_id'],
        'create_at': datetime.utcnow(),
    }

    # 保存评论
    mongo.db.comments.save(comment)

    # 增加用户回帖和帖子回复量计数
    mongo.db.users.update_one({'_id': user['_id']}, {'$inc': {'reply_count': 1}})
    mongo.db.posts.update({'_id': post_id}, {'$inc': {'comment_count': 1}})

    if post['user_id'] != current_user.user['_id']:
        # 给发帖人新增一条通知消息
        user = mongo.db.users.find_one({'_id': post['user_id']})
        add_message(user, render_template('user_message/reply_message.html', post=post, user=current_user.user, comment=comment))

    if content.startswith('@'):
        end = content.index(' ')
        username = content[1:end]
        if username != current_user.user['username']:
            user = mongo.db.users.find_one({'username': username})
            # 给被@的人新增一条通知消息
            add_message(user, render_template('user_message/reply_message.html', post=post, user=current_user.user, comment=comment))

    return jsonify(code_msg.COMMENT_SUCCESS)


@api_view.route('/reply/delete/<ObjectId:comment_id>', methods=['POST'])
@login_required
def reply_delete(comment_id):
    if not current_user.user['is_admin']:
        abort(403)
    comment = mongo.db.comments.find_one_or_404({'_id': comment_id})
    post_id = comment['post_id']
    # 更新计数
    update_action = {'$inc': {'comment_count': -1}}
    if comment['is_adopted']:
        # 如果删除的是采纳的评论恢复其他评论可采纳
        update_action['$set'] = {'accepted': False}
    # 更新帖子回帖数, 是否更新用户回帖计数在考虑中，暂未实现
    mongo.db.posts.update_one({'_id': post_id}, update_action)

    mongo.db.comments.delete_one({'_id': comment_id})
    return jsonify(code_msg.DELETE_SUCCESS)


@api_view.route('/reply/content/<ObjectId:comment_id>', methods=['POST', 'GET'])
@login_required
def get_reply_content(comment_id):
    comment = mongo.db.comments.find_one_or_404({'_id': ObjectId(comment_id)})
    return jsonify(models.R.ok(data=comment['content']))


@api_view.route('/reply/update/<ObjectId:comment_id>', methods=['POST'])
@login_required
def reply_update(comment_id):
    content = request.values.get('content')
    if not content:
        return jsonify(code_msg.POST_CONTENT_EMPTY)
    comment = mongo.db.comments.find_one_or_404({'_id': comment_id})
    if current_user.user['_id'] != comment['user_id']:
        abort(403)
    mongo.db.comments.update_one({'_id': comment_id}, {'$set': {'content': content}})
    return jsonify(models.R.ok())


@api_view.route('/post/delete/<ObjectId:post_id>', methods=['POST'])
@login_required
def post_delete(post_id):
    post = mongo.db.posts.find_one_or_404({'_id': ObjectId(post_id)})
    if post['user_id'] != current_user.user['_id'] and not current_user.user['is_admin']:
        return jsonify(code_msg.USER_UN_HAD_PERMISSION)
    mongo.db.posts.delete_one({'_id': post_id})
    mongo.db.users.update_many({}, {'$pull': {'collections': post_id}})

    # 删除检索索引
    whoosh_searcher.delete_document('posts', 'obj_id', str(post_id))
    return jsonify(code_msg.DELETE_SUCCESS.put('action', url_for('index.index', catalog_id=post['catalog_id'])))


@api_view.route('/post/set/<ObjectId:post_id>/<string:field>/<int:val>', methods=['POST'])
@login_required
def post_set(post_id, field, val):
    post = mongo.db.posts.find_one_or_404({'_id': post_id})
    if field != 'is_closed':
        if not current_user.user['is_admin']:
            return jsonify(code_msg.USER_UN_HAD_PERMISSION)
    elif current_user.user['_id'] != post['user_id'] and not current_user.user['is_admin']:
        return jsonify(code_msg.USER_UN_HAD_PERMISSION)
    val = val == 1
    mongo.db.posts.update_one({'_id': post_id}, {'$set': {field: val}})
    return jsonify(models.R.ok())


# 用户发的帖子
@api_view.route('/posts/<int:pn>/', methods=['POST', 'GET'])
@api_view.route('/posts/', methods=['POST', 'GET'])
@login_required
def post_list(pn=1):
    # posts = mongo.db.posts.find({"user_id": current_user.user['_id']})
    page = db_utils.get_page('posts', 1, sort_by=('_id', -1), filter1={"user_id": current_user.user['_id']})
    data = models.R.ok().put('rows', page.result).put('count', page.total)
    return dumps(data)


# 签到
@api_view.route('/sign', methods=['POST'])
@login_required
def user_sign():
    date = datetime.utcnow().strftime('%Y-%m-%d')
    user = current_user.user
    doc = {
        'user_id': user['_id'],
        'date': date
    }
    sign_log = mongo.db['user_signs'].find_one(doc)
    if sign_log:
        return jsonify(code_msg.REPEAT_SIGNED)
    # 随机奖励
    interval = db_utils.get_option('sign_interval', {'val': '1-100'})['val'].split('-')
    coin = random.randint(int(interval[0]), int(interval[1]))
    doc['coin'] = coin
    # print(coin)
    # 插入签到记录
    mongo.db['user_signs'].insert_one(doc)
    # 增加金币
    mongo.db.users.update({'_id': user['_id']}, {"$inc": {'coin': coin}})
    return jsonify(models.R.ok(data={'signed': True, 'coin': coin}))


@api_view.route('/sign/status', methods=['POST'])
@login_required
def sign_status():
    user = current_user.user
    sign_log = mongo.db['user_signs'].find_one({'user_id': user['_id'], 'date': datetime.utcnow().strftime('%Y-%m-%d')})
    signed = False
    coin = 0
    if sign_log:
        signed = True
        coin = sign_log.get('coin', 0)

    return jsonify(models.R.ok(data={'signed': signed, 'coin': coin}))

