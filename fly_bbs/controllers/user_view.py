from flask import Blueprint, render_template,flash, request,session,jsonify, url_for, current_app, redirect, abort
from flask_login import login_user, logout_user, login_required, current_user
from fly_bbs import utils,forms, models, db_utils
from fly_bbs.extensions import mongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash
from random import randint
from datetime import datetime
user_view = Blueprint("user", __name__, url_prefix="", template_folder="templates")

@user_view.route('/<ObjectId:user_id>')
def user_home(user_id):
    user = mongo.db.users.find_one_or_404({'_id': user_id})
    return render_template('user/home.html', user=user)

@user_view.route('/posts')
@login_required
def user_posts():
    return render_template('user/index.html', user_page='posts', page_name='user')

@user_view.route('/message')
@user_view.route('/message/page/<int:pn>')
@login_required
def user_message(pn=1):
    user = current_user.user
    if user.get('unread', 0) > 0:
        mongo.db.users.update({'_id': user['_id']}, {'$set': {'unread': 0}})
    message_page = db_utils.get_page('messages', pn, filter1={'user_id': user['_id']}, sort_by=('_id', -1))
    return render_template('user/message.html', user_page='message', page_name='user', page=message_page)

@user_view.route('/message/remove', methods=['POST'])
@login_required
def remove_message():
    user = current_user.user
    if request.values.get('all') == 'true':
        mongo.db.messages.delete_many({'user_id': user['_id']})
    elif request.values.get('id'):
        msg_id = ObjectId(request.values.get('id'))
        mongo.db.messages.delete_one({'_id': msg_id})
    return jsonify(models.BaseResult())


@user_view.route('/set', methods=['GET', 'POST'])
@login_required
def user_set():
    if request.method == 'POST':
        include_keys = ['username', 'avatar', 'desc', 'city', 'sex']
        data = request.values
        update_data = {}
        for key in data.keys():
            if key in include_keys:
                update_data[key] = data.get(key)
        # print(update_data)
        mongo.db.users.update({'_id': current_user.user['_id']}, {'$set': data})
        return jsonify(models.BaseResult())
    return render_template('user/set.html', user_page='set', page_name='user', title='基本设置')

@user_view.route('/repass', methods=['POST'])
def user_repass():
    if request.values.has_key('email'):
        email = request.values.get('email')
        ver_code = request.values.get('ver_code')
        code = request.values.get('code')
        username = request.values.get('username')
        password = request.values.get('password')
        repassword = request.values.get('repassword')
        if not (code and email and username):
            return jsonify(models.BaseResult(code=1, msg='参数错误'))
        if not utils.verify_num(ver_code):
            return jsonify(models.BaseResult(code=1, msg='验证码错误'))
        if not password or (len(password) < 6 or len(password) > 16):
            return jsonify(models.BaseResult(1, '密码不能为空或长度不符'))
        if password != repassword:
            return jsonify(models.BaseResult(1, '两次输入的密码不一致'))
        active_code = mongo.db.active_codes.find_one_or_404({'_id': ObjectId(code)})
        mongo.db.active_codes.delete_one({'_id': ObjectId(code)})
        user = mongo.db.users.update({'_id': active_code['user_id'],'email': email, 'username': username}, {'$set': {'password': generate_password_hash(password)}})
        # print(user)
        if user['nModified'] == 0:
            return jsonify(models.BaseResult(msg='密码修改失败，请联系管理员').put('action', url_for('user.login')))
        return jsonify(models.BaseResult(msg='密码修改成功').put('action', url_for('user.login')))
    if not current_user.is_authenticated:
        return redirect(url_for('user.login'))
    nowpassword = request.values.get('nowpassword')
    password = request.values.get('password')
    repassword = request.values.get('repassword')
    user = current_user.user
    if not nowpassword:
        return jsonify(models.BaseResult(1, '当前密码不能为空'))
    if not models.User.validate_login(user['password'], nowpassword):
        return jsonify(models.BaseResult(1, '密码不正确'))
    if not password or (len(password) < 6 or len(password) > 16):
        return jsonify(models.BaseResult(1, '密码不能为空或长度不符'))
    if password != repassword:
        return jsonify(models.BaseResult(1, '两次输入的密码不一致'))
    mongo.db.users.update({'_id': user['_id']}, {'$set': {'password': generate_password_hash(password)}})
    return jsonify(models.BaseResult())


@user_view.route('/forget', methods=['POST', 'GET'])
@user_view.route('/forget/<ObjectId:code>', methods=['POST', 'GET'])
def user_pass_forget(code=None):
    if request.method == 'POST':
        email = request.values.get('email')
        ver_code = request.values.get('ver_code')
        if not email:
            return jsonify(models.BaseResult(code=1, msg='邮箱不能为空'))
        if not utils.verify_num(ver_code):
            return jsonify(models.BaseResult(code=1, msg='验证码错误'))
        user = mongo.db.users.find_one({'email': email})
        if not user:
            return jsonify(models.BaseResult(code=1, msg='邮箱未注册'))
        send_active_email(user['username'], user_id=user['_id'], email=email, is_forget=True)
        return jsonify(models.BaseResult(msg='密码重置邮件已发送，请前往邮箱查看').put('action', url_for('user.login')))
    has_code = False
    user = None
    if code:
        active_code = mongo.db.active_codes.find_one({'_id': code})
        has_code = True
        if not active_code:
            return render_template('user/forget.html', page_name='user', has_code=True, code_invalid=True)
        user = mongo.db.users.find_one({'_id': active_code['user_id']})

    ver_code = utils.gen_verify_num()
    # session['ver_code'] = ver_code['answer']
    return render_template('user/forget.html', page_name='user', ver_code=ver_code['question'], code=code, has_code=has_code, user=user)


def send_active_email(username, user_id, email, is_forget=False):
    code = mongo.db.active_codes.insert_one({'user_id': user_id})
    if is_forget:
        body = render_template('email/user_repwd.html', url=url_for('user.user_pass_forget', code=code.inserted_id, _external=True))
        utils.send_email(email, '重置密码', body=body)
        return
    body = render_template('email/user_activate.html', username=username,
                           url=url_for('user.user_active', code=code.inserted_id, _external=True))
    utils.send_email(email, '账号激活', body=body)

@user_view.route('/active', methods=['GET', 'POST'])
def user_active():
    if request.method == 'GET':
        code = request.values.get('code')
        if code:
            user_id = mongo.db.active_codes.find_one({'_id': ObjectId(code)})['user_id']
            if user_id:
                mongo.db.active_codes.delete_many({'user_id': ObjectId(user_id)})
                mongo.db.users.update({'_id': user_id}, {"$set": {'is_active': True}})
                user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
                login_user(models.User(user))
                return render_template('user/activate.html')
        if not current_user.is_authenticated:
            abort(403)
        return render_template('user/activate.html')
    if not current_user.is_authenticated:
        abort(403)
    user = current_user.user
    mongo.db.active_codes.delete_many({'user_id': ObjectId(user['_id'])})
    send_active_email(user['username'], user['_id'], user['email'])
    return jsonify(models.R().ok().put('msg', '重新发送邮件成功, 请前往您的邮箱查看邮件激活你的账号').put('action', url_for('user.active')))


@user_view.route('/reg', methods=['GET','POST'])
def register():
    if db_utils.get_option('open_user', {}).get('val') != '1':
        abort(404)
    user_form = forms.RegisterForm()
    if user_form.is_submitted():
        if not user_form.validate():
            return jsonify(models.BaseResult(1, str(user_form.errors)))
        if not utils.verify_num(user_form.vercode.data):
            return jsonify(models.BaseResult(1, str('验证码错误')))
        user = mongo.db.users.find_one({'email': user_form.email.data})
        if user:
            return jsonify(models.BaseResult(1, '该邮箱已注册'))
        user = dict({
            'is_active': False,
            'coin': 0,
            'email': user_form.email.data,
            'username': user_form.username.data,
            'vip': 0,
            'reply_count': 0,
            'avatar': url_for('static', filename='images/avatar/' + str(randint(0, 12)) + '.jpg'),
            'password': generate_password_hash(user_form.password.data),
            'create_at': datetime.utcnow()
        })
        mongo.db.users.insert_one(user)
        send_active_email(user['username'], user['_id'], user['email'])
        return jsonify(models.R().ok().put('msg', '用户注册成功, 请前往您的注册邮箱查看邮件激活你的账号后登录').put('action',url_for('user.login')))
    ver_code = utils.gen_verify_num()
    # session['ver_code'] = ver_code['answer']
    return render_template('user/reg.html', ver_code=ver_code['question'], form=user_form)


@user_view.route('/login', methods=['GET','POST'])
def login():
    user_form = forms.LoginForm()
    if user_form.is_submitted():
        if not user_form.validate():
            return jsonify(models.BaseResult(1, str(user_form.errors)))
        if not utils.verify_num(user_form.vercode.data):
            return jsonify(models.BaseResult(1, '验证码错误'))
        user = mongo.db.users.find_one({'email': user_form.email.data})
        if not models.User.validate_login(user['password'], user_form.password.data):
            return jsonify(models.BaseResult(1, '密码错误'))
        if not user.get('is_active', False):
            return jsonify(models.BaseResult(1, '账号未激活'))
        if user.get('is_disabled', False):
            return jsonify(models.BaseResult(1, '账号已被禁用'))
        login_user(models.User(user))
        action = request.values.get('next')
        if not action:
            action = url_for('index.index')
        return jsonify(models.R().ok().put('msg', '登录成功').put('action', action))
    logout_user()
    ver_code = utils.gen_verify_num()
    # session['ver_code'] = ver_code['answer']
    return render_template('user/login.html', ver_code=ver_code['question'], form=user_form)

@user_view.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

