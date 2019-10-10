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


class AssetReportForm(FlaskForm):
    details =    StringField('Details', validators=[DataRequired(),Length(min=20)])
    submitter =  StringField('Submitter', validators=[DataRequired()],render_kw={"placeholder": "Your Kerberos ID (ex smithj01)"})
    new_status = HiddenField('new_status', validators=[DataRequired()])

class InstructionTemplateForm(ModelForm):
    class Meta:
        model = InstructionTemplate
InstructionTemplate.form = InstructionTemplateForm

class AssetEditForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super(AssetEditForm, self).__init__(*args,**kwargs)
        self.instruction_template.query = InstructionTemplate.query

    class Meta:
        model = Asset
        exclude = ['status', 'shortcode']
    instruction_template = QuerySelectField('Instructions template',get_label=lambda x:x.name)
Asset.form = AssetEditForm


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