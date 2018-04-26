from flask_mail import Message
from fly_bbs.config import MailConfig
import fly_bbs
def send_email(to, subject):
    msg = Message(subject=MailConfig.MAIL_SUBJECT_PREFIX + subject , sender=MailConfig.MAIL_SENDER, recipients=[to])
    msg.body = "测试测试"
    msg.html = "<a href='://baidu.com'>点击打开百度</a>"
    print(fly_bbs.mongodb)
    fly_bbs.mail.send(msg)
