from flask_wtf import FlaskForm
from wtforms import fields
from wtforms.validators import DataRequired, Email, EqualTo,Length, InputRequired

class RegisterForm(FlaskForm):
    email = fields.StringField(validators=[DataRequired('邮箱不能为空'), Email('邮箱格式不正确')])
    username = fields.StringField(validators=[DataRequired('昵称不能为空')])
    vercode = fields.StringField(validators=[InputRequired('验证码不能为空')])
    password = fields.PasswordField(validators=[DataRequired('密码不能为空'), Length(min=6, max=16, message='密码长度应该在6-16之间')])
    re_password = fields.PasswordField(validators=[DataRequired('重复密码不能为空'),EqualTo('password', '两次输入的密码不一致')])
    #desc = fields.StringField()

class LoginForm(FlaskForm):
    email = fields.StringField(validators=[DataRequired('邮箱不能为空')])
    vercode = fields.StringField(validators=[InputRequired('验证码不能为空')])
    password = fields.PasswordField(validators=[DataRequired('密码不能为空')])

class PostsForm(FlaskForm):
    id = fields.StringField()
    title = fields.StringField(validators=[DataRequired('标题不能为空')])
    content = fields.StringField(validators=[DataRequired('正文不能为空')])
    catalog_id = fields.StringField(validators=[DataRequired('所属专栏不能为空')])
    reward = fields.IntegerField(validators=[InputRequired('悬赏金币不能为空')])
    vercode = fields.StringField(validators=[InputRequired('验证码不能为空')])
