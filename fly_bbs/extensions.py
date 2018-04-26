from flask_mail import Mail
from flask_admin import Admin
from flask_login import LoginManager
import pymongo
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
from fly_bbs.models import User
from fly_bbs.controllers import admin as admin_view
from flask_uploads import UploadSet, configure_uploads
# 初始化Mail
mail = Mail()
# 初始化Flask-Admin
admin = Admin(name='PyFly 后台管理')
mongo = PyMongo()
login_manager = LoginManager()
login_manager.login_view = 'user.login'

upload_photos = UploadSet('photos')

@login_manager.user_loader
def load_user(user_id):
    u = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if not u:
        return None
    return User(u)

def init_extensions(app):
    configure_uploads(app, upload_photos)
    mail.init_app(app)
    admin.init_app(app)
    mongo.init_app(app, "MONGO")
    login_manager.init_app(app)
    with app.app_context():
        admin.add_view(admin_view.UsersModelView(mongo.db['users'], '用户管理'))
        admin.add_view(admin_view.CatalogsModelView(mongo.db['catalogs'], '栏目管理'))
        admin.add_view(admin_view.PostsModelView(mongo.db['posts'], '帖子管理'))
        admin.add_view(admin_view.PassagewaysModelView(mongo.db['passageways'], '温馨通道'))
        admin.add_view(admin_view.FriendLinksModelView(mongo.db['friend_links'], '友链管理'))
        admin.add_view(admin_view.PagesModelView(mongo.db['pages'], '页面管理'))
        admin.add_view(admin_view.FooterLinksModelView(mongo.db['footer_links'], '底部链接'))
        admin.add_view(admin_view.AdsModelView(mongo.db['ads'], '广告管理'))
        admin.add_view(admin_view.OptionsModelView(mongo.db['options'], '系统设置'))
