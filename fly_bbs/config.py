import os
from flask_uploads import IMAGES
class Dev:
    MONGO_URI = "mongodb://127.0.0.1:27017/pyfly"
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PROT = 465
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'xiuqianli_2015@163.com'
    MAIL_PASSWORD = 'asdf1234'
    MAIL_DEBUG = True
    MAIL_SUBJECT_PREFIX = '[PyFly]-'

    UPLOADED_PHOTOS_ALLOW = IMAGES
    UPLOADED_PHOTOS_DEST = os.getcwd() + '/uploads'

class Pud:
    pass

config = {
    "Dev": Dev,
    "Pud": Pud
}