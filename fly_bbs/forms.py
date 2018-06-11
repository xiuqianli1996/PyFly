from flask_wtf import FlaskForm
from wtforms import fields
from wtforms.validators import DataRequired, Email, EqualTo, Length, InputRequired
from fly_bbs import code_msg


class RegisterForm(FlaskForm):
    email = fields.StringField(validators=[DataRequired(code_msg.EMAIL_EMPTY.get_msg()),
                                           Email(code_msg.EMAIL_ERROR.get_msg())])
    username = fields.StringField(validators=[DataRequired(code_msg.USERNAME_EMPTY.get_msg())])
    vercode = fields.StringField(validators=[InputRequired(code_msg.VERIFY_CODE_ERROR.get_msg())])
    password = fields.PasswordField(validators=[Length(min=6, max=16, message=code_msg.PASSWORD_LENGTH_ERROR.get_msg())])
    re_password = fields.PasswordField(validators=[EqualTo('password', code_msg.PASSWORD_REPEAT_ERROR.get_msg())])
    # desc = fields.StringField()


class LoginForm(FlaskForm):
    email = fields.StringField(validators=[DataRequired(code_msg.EMAIL_EMPTY.get_msg())])
    vercode = fields.StringField(validators=[InputRequired(code_msg.VERIFY_CODE_ERROR.get_msg())])
    password = fields.PasswordField(validators=[DataRequired(code_msg.PASSWORD_LENGTH_ERROR.get_msg())])


class PostsForm(FlaskForm):
    id = fields.StringField()
    title = fields.StringField(validators=[DataRequired(code_msg.POST_TITLE_EMPTY.get_msg())])
    content = fields.StringField(validators=[DataRequired(code_msg.POST_CONTENT_EMPTY.get_msg())])
    catalog_id = fields.StringField(validators=[DataRequired(code_msg.POST_CATALOG_EMPTY.get_msg())])
    reward = fields.IntegerField(validators=[InputRequired(code_msg.POST_COIN_EMPTY.get_msg())])
    vercode = fields.StringField(validators=[InputRequired(code_msg.VERIFY_CODE_ERROR.get_msg())])


class ForgetPasswordForm(FlaskForm):
    email = fields.StringField(validators=[DataRequired(code_msg.EMAIL_EMPTY.get_msg())])
    code = fields.StringField(validators=[DataRequired(code_msg.VERIFY_CODE_ERROR.get_msg())])
    vercode = fields.StringField(validators=[InputRequired(code_msg.VERIFY_CODE_ERROR.get_msg())])
    password = fields.PasswordField(
        validators=[Length(min=6, max=16, message=code_msg.PASSWORD_LENGTH_ERROR.get_msg())])
    repassword = fields.PasswordField(validators=[EqualTo('password', code_msg.PASSWORD_REPEAT_ERROR.get_msg())])


class SendForgetMailForm(FlaskForm):
    email = fields.StringField(validators=[DataRequired(code_msg.EMAIL_EMPTY.get_msg())])
    vercode = fields.StringField(validators=[InputRequired(code_msg.VERIFY_CODE_ERROR.get_msg())])


class ChangePassWordForm(FlaskForm):
    nowpassword = fields.StringField(validators=[DataRequired(code_msg.NOW_PASSWORD_EMPTY.get_msg())])
    password = fields.PasswordField(
        validators=[Length(min=6, max=16, message=code_msg.PASSWORD_LENGTH_ERROR.get_msg())])
    repassword = fields.PasswordField(validators=[EqualTo('password', code_msg.PASSWORD_REPEAT_ERROR.get_msg())])
