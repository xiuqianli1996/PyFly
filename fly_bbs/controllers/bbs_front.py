from flask import Blueprint, render_template,flash, request, url_for, current_app, session, jsonify, abort, redirect
from fly_bbs import db_utils, utils, forms, models
from fly_bbs.extensions import mongo, whoosh_searcher
from flask_login import login_required
from flask_login import current_user
from bson.objectid import ObjectId
import pymongo
from datetime import datetime
from whoosh import query,sorting, qparser


bbs_index = Blueprint("index", __name__, url_prefix="", template_folder="templates")

@bbs_index.route('/')
@bbs_index.route('/page/<int:pn>/size/<int:size>')
@bbs_index.route('/page/<int:pn>')
@bbs_index.route("/catalog/<ObjectId:catalog_id>")
@bbs_index.route("/catalog/<ObjectId:catalog_id>/page/<int:pn>")
@bbs_index.route("/catalog/<ObjectId:catalog_id>/page/<int:pn>/size/<int:size>")
def index(pn=1, size=10, catalog_id=None):
    # flash("asdsdsad")
    #print(datetime.now())
    sort_key = request.values.get('sort_key', '_id')
    sort_by = (sort_key, pymongo.DESCENDING)
    post_type = request.values.get('type')
    filter1 = {}
    if post_type == 'not_closed':
        filter1['is_closed'] = {'$ne': True}
    if post_type == 'is_closed':
        filter1['is_closed'] = True
    if post_type == 'is_cream':
        filter1['is_cream'] = True
    if catalog_id:
        filter1['catalog_id'] = catalog_id
    page = db_utils.get_page('posts', pn=pn, filter1=filter1, size=size, sort_by=sort_by)
    #print(page)
    return render_template("post_list.html", is_index=catalog_id is None, page=page, sort_key=sort_key
                           , catalog_id=catalog_id, post_type=post_type)

@bbs_index.route('/add', methods=['GET', 'POST'])
@bbs_index.route('/edit/<ObjectId:post_id>', methods=['GET', 'POST'])
@login_required
def add(post_id=None):
    posts_form = forms.PostsForm()
    if posts_form.is_submitted():
        if not posts_form.validate():
            return jsonify(models.BaseResult(1, str(posts_form.errors)))
        if not utils.verify_num(posts_form.vercode.data):
            return jsonify(models.BaseResult(1, str('验证码错误')))

        user = current_user.user
        if not user.get('is_active', False) or user.get('is_disabled', False):
            return jsonify(models.BaseResult(1, '账号未激活或已被禁用'))

        user_coin = user.get('coin', 0)
        if posts_form.reward.data > user_coin:
            return jsonify(models.BaseResult(1, '悬赏金币不能大于拥有的金币，当前账号金币为：' + str(user_coin)))
        posts = {
            'title': posts_form.title.data,
            'catalog_id': ObjectId(posts_form.catalog_id.data),
            # 'is_closed': False,
            'content': posts_form.content.data,
        }

        post_index = posts.copy()
        post_index['catalog_id'] = str(posts['catalog_id'])

        msg = '发帖成功！'
        reward = posts_form.reward.data
        if post_id:
            posts['modify_at'] = datetime.now()
            mongo.db.posts.update_one({'_id': post_id}, {'$set': posts})
            msg = '修改成功！'

        else:
            posts['create_at'] = datetime.utcnow()
            posts['reward'] = reward
            posts['user_id'] = user['_id']
            # 扣除用户发帖悬赏
            if reward > 0:
                mongo.db.users.update_one({'_id': user['_id']}, {'$inc': {'coin': -reward}})
            mongo.db.posts.save(posts)
            post_id = posts['_id']

        # 更新索引文档
        update_index(mongo.db.posts.find_one_or_404({'_id': post_id}))

        return jsonify(models.R().ok().put('msg', msg).put('action',url_for('index.index')))
    else:
        ver_code = utils.gen_verify_num()
        # session['ver_code'] = ver_code['answer']
        posts = None
        if post_id:
            posts = mongo.db.posts.find_one_or_404({'_id': post_id})
        title = '发帖' if post_id is None else '编辑帖子'
        return render_template('jie/add.html', page_name='jie', ver_code=ver_code['question'], form=posts_form, is_add=(post_id is None), post=posts, title=title)

def update_index(post):
    _id = str(post['_id'])

    post_index = dict()
    post_index['catalog_id'] = str(post['catalog_id'])
    post_index['user_id'] = str(post['user_id'])
    post_index['create_at'] = post['create_at']
    post_index['content'] = post['content']
    post_index['title'] = post['title']

    whoosh_searcher.update_document('posts', {'obj_id': _id}, post_index)

@bbs_index.route('/post/<ObjectId:post_id>/')
@bbs_index.route('/post/<ObjectId:post_id>/page/<int:pn>/')
def post_detail(post_id, pn=1):
    post = mongo.db.posts.find_one_or_404({'_id': post_id})
    if post:
        post['view_count'] = post.get('view_count', 0) + 1
        mongo.db.posts.save(post)
    post['user'] = db_utils.find_one('users', {'_id': post['user_id']}) or {}

    page = db_utils.get_page('comments', pn=pn, size=10, filter1={'post_id': post_id}, sort_by=('is_adopted', -1))
    return render_template('jie/detail.html', post=post, title=post['title'], page_name='jie', comment_page=page, catalog_id=post['catalog_id'])

@bbs_index.route('/jump')
def jump_user():
    username = request.values.get('username')
    if not username:
        abort(404)
    user = mongo.db.users.find_one_or_404({'username': username})
    return redirect('/user/' + str(user['_id']))

@bbs_index.route('/comment/<ObjectId:comment_id>/')
def jump_comment(comment_id):
    comment = mongo.db.comments.find_one_or_404({'_id': comment_id})
    post_id = comment['post_id']
    pn = 1
    if not comment.get('is_adopted',False):
        comment_index = mongo.db.comments.count({'post_id': post_id, '_id': {'$lt': comment_id}})
        pn = comment_index / 10
        if pn == 0 or pn % 10 != 0:
            pn +=  1
    return redirect(url_for('index.post_detail', post_id=post_id, pn=pn) + '#item-' + str(comment_id))
    # return redirect('/post/' + str(post_id)  + '/' + str(pn) + '/')

@bbs_index.route('/search')
@bbs_index.route('/search/page/<int:pn>/')
def post_search(pn=1, size=10):
    keyword = request.values.get('kw')
    if keyword is None:
        return render_template('search/list.html', title='搜索', message='搜索关键字不能为空!')
    with whoosh_searcher.get_searcher('posts') as searcher:
        # q = query.Or([query.Term('title', keyword), query.Term('content', keyword)])
        parser = qparser.MultifieldParser(['title', 'content'], whoosh_searcher.get_index('posts').schema)
        q = parser.parse(keyword)
        result = searcher.search_page(q, pagenum=pn, pagelen=size, sortedby=sorting.ScoreFacet())
        result_list = [x.fields() for x in result.results]
        page = models.Page(pn, size, result=result_list, has_more=result.pagecount > pn, total_page=result.pagecount
                           , total=result.total)
        print(page.result)
    # return jsonify(page)
    return render_template('search/list.html', title=keyword + '搜索结果', page=page, kw=keyword)

@bbs_index.route('/refresh/indexes')
def refresh_indexes():
    name = request.values.get('name')
    whoosh_searcher.clear(name)
    writer = whoosh_searcher.get_writer(name)
    for item in mongo.db[name].find({}, ['_id', 'title', 'content', 'create_at', 'user_id', 'catalog_id']):
        item['obj_id'] = str(item['_id'])
        item['user_id'] = str(item['user_id'])
        item['catalog_id'] = str(item['catalog_id'])
        item.pop('_id')
        writer.add_document(**item)
    writer.commit()
    return ''

