from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField
class Post_form(FlaskForm):
    title = StringField(u'Add Title to your blog', validators=[DataRequired()])
    subtitle = StringField(u'Add a Subtitle', validators=[DataRequired()])
    content = CKEditorField(u'Body')
    img_url = StringField(u'Image URL', validators=[DataRequired(), URL()])
    submit = SubmitField("Submit Post")

class RegistrationForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

class Comment_Form(FlaskForm):
    user_comment = CKEditorField('Comments', validators=[DataRequired()])
    submit = SubmitField()
