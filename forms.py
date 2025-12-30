from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, URL, Length, Regexp, Optional
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

# TODO: Create a RegisterForm to register new users
class RegistrationForm(FlaskForm):
    user_name = StringField(label="User name",validators=[DataRequired()])
    email = EmailField(label="Email",validators=[DataRequired()])
    password = StringField(label="Password",validators=[DataRequired()])
    submit = SubmitField("Register")

# TODO: Create a LoginForm to login existing users
class LoginForm(FlaskForm):
    email = EmailField(label="Email",validators=[DataRequired()])
    password = StringField(label="Password",validators=[DataRequired()])
    submit = SubmitField("Login")

# TODO: Create a CommentForm so users can leave comments below posts
class CommentForm(FlaskForm):
    comment = CKEditorField("Leave a comment", validators=[DataRequired()])
    submit = SubmitField("Submit")

# TODO: Create a Contacts form
class ContactForm(FlaskForm):
    name = StringField(label="Name",validators=[Length(max=40), DataRequired()])
    company = StringField(label="Company",validators=[Length(max=40),Optional()])
    email = StringField(label="Contact Email",validators=[Length(max=40),DataRequired()])
    phone_number = StringField(label="Cellphone Number",validators=[Optional(),Length(min=10,max=14),Regexp(r'^[+0-9-]+$',message='Invalid Phone number format')])
    message = TextAreaField(label="Message",validators=[Length(max=1000),DataRequired()])
    submit = SubmitField(label='Submit')
