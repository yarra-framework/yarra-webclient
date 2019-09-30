from wtforms import StringField,HiddenField,SelectField,TextAreaField,PasswordField
from jinja2 import Template
from datetime import datetime
import enum
from extensions import db


class AssetStatus(enum.Enum):
    up = 0
    down = 1
    unknown = 2

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    roles = db.relationship('Role', secondary='user_roles')

    @classmethod
    def get_id_field(self):
        return 'id'

    def get_id(self):
        return self.id

    def __str__(self):
        return "<User {}>".format(self.username)
    

# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

class InstructionTemplate(db.Model):
    id =      db.Column(db.Integer, primary_key=True)
    name =      db.Column(db.String,nullable=False,default="",unique=True, info={'label':'Name'})
    text =      db.Column(db.String,nullable=False,default="",info={'label':'Text','form_field_class': TextAreaField})
    assets = db.relationship('Asset', backref='instruction_template', lazy=True)

    @classmethod
    def get_id_field(self):
        return 'name'
    def get_id(self):
        return self.name

    def __repr__(self):
        return '<InstructionTemplate %r>' % self.name

class Asset(db.Model):
    def generate_shortcode():
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))

    def render_instructions(self):
        return Template(self.instruction_template.text).render(asset=self)

    id =        db.Column(db.Integer, primary_key=True)
    name =      db.Column(db.String(80),  unique=True,  nullable=False, default="",info={'label':'Name'})
    building =  db.Column(db.String(120), unique=False, nullable=False, default="",info={'label':'Building'})
    location =  db.Column(db.String(120), unique=False, nullable=True, info={'label':'Location'})
    type =      db.Column(db.String(4),   unique=False, nullable=False, default="",info={'label':'Type'})

    make =      db.Column(db.String(50),  unique=False, nullable=True, info={'label':'Make'})
    model =     db.Column(db.String(50),  unique=False, nullable=True, info={'label':'Model'})
    software_version = db.Column(db.String(50),   unique=False, nullable=True, info={'label':'Software version'})
    serial =    db.Column(db.String(50),  unique=False, nullable=True, info={'label':'Serial'})

    shortcode = db.Column(db.String(10),        unique=True,  nullable=False, default=generate_shortcode)
    status =    db.Column(db.Enum(AssetStatus), unique=False, nullable=False, default=AssetStatus.up)
    status_changed = db.Column(db.DateTime, nullable=False, default = datetime.now)
    events = db.relationship('StatusEvent', backref='asset', lazy=True)
    instruction_template_id = db.Column(db.Integer, db.ForeignKey('instruction_template.id'), nullable=True)
    asset_instructions = db.Column(db.String,        unique=False,  nullable=True)

    @classmethod
    def get_id_field(self):
        return 'shortcode'

    def get_id(self):
        return self.shortcode

    def set_status(self,new_status,**kwargs):
        event = StatusEvent(new_status=new_status, old_status = self.status,asset = self, **kwargs)
        db.session.add(event)
        if self.status != new_status:
            self.status_changed = datetime.now()
        self.status = new_status

    def __repr__(self):
        return '<Asset %r>' % self.name


class StatusEvent(db.Model):
    id = 		 db.Column(db.Integer, primary_key=True)
    timestamp =  db.Column(db.DateTime, nullable=False, default = datetime.now)
    new_status = db.Column(db.Enum(AssetStatus),nullable=False)
    old_status = db.Column(db.Enum(AssetStatus),nullable=False)
    asset_id =   db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    details =    db.Column(db.String,nullable=False)
    submitter =  db.Column(db.String,nullable=False)

    def __repr__(self):
        return '<StatusEvent %r>' % self.timestamp
