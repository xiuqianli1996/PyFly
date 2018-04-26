from flask import Flask
from fly_bbs.controllers import config_blueprint
from .custom_functions import init_func
from fly_bbs.config import config
from fly_bbs.extensions import init_extensions
from fly_bbs import db_utils
from fly_bbs.install_init import init as install_init


# app.config.update(DEBUG = True,
#     MAIL_SERVER='smtp.qq.com',
#     MAIL_PROT=465,
#     MAIL_USE_TLS = True,
#     MAIL_USE_SSL = False,
#     MAIL_USERNAME = '邮箱地址',
#     MAIL_PASSWORD  = '',#从系统中获取授权码
#     MAIL_DEBUG = True)


# 初始化模板全局函数


def create_app(config_name):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'PyFly123'
    app.config.from_object(config[config_name])
    init_extensions(app)
    init_func(app)
    config_blueprint(app)
    with app.app_context():
        app.config['MAIL_SUBJECT_PREFIX'] = db_utils.get_option('mail_prefix') or app.config['MAIL_SUBJECT_PREFIX']
        install_init()
    return app