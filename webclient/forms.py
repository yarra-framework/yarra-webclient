from flask_wtf import FlaskForm
from wtforms.validators import *
from wtforms import StringField,HiddenField,SelectField,TextAreaField,PasswordField
from lib.wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms import widgets
from models import *
from wtforms_alchemy import model_form_factory, ModelFormField

BaseModelForm = model_form_factory(FlaskForm)

class ModelForm(BaseModelForm):
    pass
    # @classmethod
    # def get_session(self):
    #     return db.session

class NewForm(ModelForm):
    pass

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(),Length(min=3), Regexp(r'^\w+$',message='Invalid username: must be lowercase alphanumeric')])
    email = StringField('Email', validators=[InputRequired(),Email()])
    password = PasswordField('Password', validators=[InputRequired(),Length(min=6),EqualTo('password_confirm',message='Passwords must match')])
    password_confirm = PasswordField('Password (confirm)', validators=[InputRequired(), Length(min=6)])

class PasswordChangeForm(FlaskForm):
    old_password = PasswordField('Current password', validators=[InputRequired()])
    password = PasswordField('New password', validators=[InputRequired(),Length(min=6),EqualTo('password_confirm',message='Passwords must match')])
    password_confirm = PasswordField('New password (confirm)', validators=[InputRequired(), Length(min=6)])


class UserForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super(UserForm, self).__init__(*args,**kwargs)
        self.roles.query = Role.query

    class Meta:
        model = User
        exclude = ['password', 'username']
    
    email = StringField('Email', validators=[InputRequired(),Email()])    
    roles = QuerySelectMultipleField('Roles',get_label=lambda x:x.name,
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput())
    

User.form = UserForm

class ServerForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super(ServerForm, self).__init__(*args,**kwargs)
        self.roles.query = Role.query

    class Meta:
        model = YarraServer
    
    path = StringField('Path', validators=[InputRequired()])
    username = StringField('username', validators=[InputRequired()])
    password = StringField('password', validators=[InputRequired()])
    

    roles = QuerySelectMultipleField('Roles',get_label=lambda x:x.name,
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput())

YarraServer.form = ServerForm


class RoleForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super(RoleForm, self).__init__(*args,**kwargs)
        self.servers.query = YarraServer.query
        self.users.query = User.query

    class Meta:
        model = Role

    name = StringField('Name', validators=[InputRequired()], render_kw={'readonly': True})
    servers = QuerySelectMultipleField('Servers',get_label=lambda x:x.name,
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput())

    users = QuerySelectMultipleField('Users',get_label=lambda x:x.username,
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput())

Role.form = RoleForm