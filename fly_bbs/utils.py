import json
import random
from bson import ObjectId
from flask_mail import Message
from . import extensions, models
from threading import Thread
from flask import current_app, session, request


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def verify_num(code):
    from .code_msg import VERIFY_CODE_ERROR

    if code != session['ver_code']:
        raise models.GlobalApiException(VERIFY_CODE_ERROR)
    # return result


def gen_verify_num():
    a = random.randint(-20, 20)
    b = random.randint(0, 50)
    data = {'question': str(a) + ' + ' + str(b) + " = ?", 'answer': str(a + b)}
    session['ver_code'] = data['answer']
    return data


def gen_cache_key():
    return 'view//' + request.full_path


def send_mail_async(app, msg):
    with app.app_context():
        extensions.mail.send(msg)


def send_email(to, subject, body, is_txt=True):
    app = current_app._get_current_object()
    msg = Message(subject=app.config.get('MAIL_SUBJECT_PREFIX') + subject, sender=app.config.get('MAIL_USERNAME'), recipients=[to])
    if is_txt:
        msg.body = body
    else:
        msg.html = body
    thr = Thread(target=send_mail_async, args=[app, msg])
    thr.start()
    return thr
