from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField
class Post_form(FlaskForm):
    title = StringField(u'Add Title to your blog', validators=[DataRequired()])
    subtitle = StringField(u'Add a Subtitle', validators=[DataRequired()])
    content = CKEditorField(u'Body')
    img_url = StringField(u'Image URL', validators=[DataRequired(), URL()])
    submit = SubmitField("Publish Post")

class RegistrationForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    email = StringField("Email address", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email address", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class Comment_Form(FlaskForm):
    user_comment = CKEditorField('Comments', validators=[DataRequired()])
    submit = SubmitField()

class Contact_Form(FlaskForm):
    phone_number = StringField(u'Phone Number')
    message = CKEditorField(u'Message', validators=[DataRequired()])
    submit = SubmitField(u'Send message')
