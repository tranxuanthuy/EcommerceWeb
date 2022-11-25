from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
import email_validator
from website.models import User

class LoginForm(FlaskForm):
    email = StringField(label="Email", \
        validators=[DataRequired(), Email()])
    password = PasswordField(label="Mật khẩu", \
        validators=[DataRequired(), Length(min=2, max=10)])
    remember_me = BooleanField(label="Ghi nhớ tôi")
    submit = SubmitField(label="Đăng nhập")

class RegisterForm(FlaskForm):
    email = StringField(label="Email", \
        validators=[DataRequired(), Email()])
    username = StringField(label="Họ và tên", \
        validators=[DataRequired()])
    password = PasswordField(label="Mật khẩu", \
        validators=[DataRequired(), Length(min=3, max=10)])
    repeat_password = PasswordField(label="Xác nhận mật khẩu", \
        validators=[DataRequired(), Length(min=3, max=10), EqualTo("password")])
    submit = SubmitField(label="Đăng kí")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Vui lòng dùng một địa chỉ email khác.')