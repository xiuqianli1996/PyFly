from flask import Blueprint, render_template,flash, request,session,jsonify, url_for, current_app, redirect, abort
from fly_bbs.extensions import oauth_weibo

oauth_view = Blueprint('oauth', __name__, url_prefix='', template_folder='templates')


@oauth_view.route('/weibo/login')
def weibo_login():
    return oauth_weibo.authorize(callback=url_for('oauth.weibo_authorized',_external=True))

@oauth_view.route('/weibo/login/authorized')
def weibo_authorized():
    resp = oauth_weibo.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    return redirect(url_for('index'))