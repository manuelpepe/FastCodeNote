################### FORMS FILE ###################
#
#                  Forms clases
#
######################################################

from wtforms import Form, TextField, TextAreaField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo

# Signup Form
class SignupForm(Form):
    username = TextField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired(), EqualTo('confirm', message = 'Passwords must match')])
    confirm = PasswordField('Confirm Password', validators = [DataRequired()])
    email = TextField('Email')
    accept_tos = BooleanField('Accept TOS', validators = [DataRequired()], default = False)

# Login Form
class LoginForm(Form):
    username = TextField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember = BooleanField('Remember me', default = False)

# Add Snippet Form
class AddSnippetForm(Form):
    language = SelectField('Laguage', choices = [('C', 'C'), ('C#', 'C#'), ('C++', 'C++'), ('CSS', 'CSS'), ('HTML', 'HTML'), \
                                                ('Java', 'Java'), ('JavaScript', 'JavaScript'), ('PHP', 'PHP'), ('Python', 'Python'), \
                                                ('Ruby', 'Ruby'), ('SQL', 'SQL'), ('Visual Basic', 'Visual Basic'), ('Text', 'Plain Text')])
    title = TextField('Title', validators = [DataRequired()])
    description = TextField('Description', validators = [DataRequired()])
    content = TextAreaField('Snippet Content', validators = [DataRequired()])

class AddGroupForm(Form):
    name = TextField('Name', validators = [DataRequired()]) 
    description = TextField('Description', validators = [DataRequired()])   

class ContactForm(Form):
    name = TextField('Name', validators = [DataRequired()])
    email = TextField('Email', validators = [DataRequired()])
    subject = TextField('Subject', validators = [DataRequired()])
    body = TextAreaField('Content', validators = [DataRequired()])

class CommentForm(Form):
    content = TextAreaField('Comment', validators = [DataRequired()])