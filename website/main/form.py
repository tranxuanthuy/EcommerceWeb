from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange

CATEGORIES = ["Xe cộ", "Đồ điện tử",\
        "Thời trang", "Văn phòng phẩm", "Khác"]

class EditProfile(FlaskForm):
    username = StringField(label="Họ và tên", validators=[DataRequired()])
    about_me = TextAreaField(label="Mô tả", validators=[Length(min=0, max=140)])
    submit = SubmitField(label="Lưu")

class PostForm(FlaskForm):
    title = TextAreaField(label="Mô tả ngắn", validators=[Length(min=1, max=140)])
    image_url = StringField(label="Đường dẫn ảnh")
    category = SelectField(label="Danh mục", choices=CATEGORIES)
    price = IntegerField(label="Giá (ngàn VND)", validators=[NumberRange(min=0, max=100000)])
    detail = TextAreaField(label="Mô tả chi tiết")

    submit = SubmitField(label="Đăng")

class CommentForm(FlaskForm):
    comment = TextAreaField(label="Bình luận", validators=[Length(min=1, max=140)])
    submit = SubmitField(label="Đăng")

class PostUpdate(FlaskForm):
    title = TextAreaField(label="Mô tả ngắn", validators=[Length(min=1, max=140)])
    image_url = StringField(label="Đường dẫn ảnh")
    category = SelectField(label="Danh mục", choices=CATEGORIES)
    price = IntegerField(label="Giá (ngàn VND)", validators=[NumberRange(min=0, max=100000)])
    detail = TextAreaField(label="Mô tả chi tiết")
    status = SelectField(label="Tình trạng", choices=['Chưa bán', 'Đã bán'])
    
    submit = SubmitField(label='Lưu')
