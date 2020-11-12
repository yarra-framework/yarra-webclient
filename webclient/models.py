from wtforms import StringField,HiddenField,SelectField,TextAreaField,PasswordField
from jinja2 import Template
from datetime import datetime
import enum
from extensions import db
from configparser import ConfigParser
import io
from yarrapyclient.serverconnection import ServerConnection
from yarrapyclient.yarraclient import Priority
from enum import Enum
from sqlalchemy_utc import utcnow, UtcDateTime 

from sqlalchemy.ext.declarative import declarative_base
from flask_jsontools import JsonSerializableBase
Base = declarative_base(cls=(JsonSerializableBase,))


class yasArchive(db.Model,Base):
    __bind_key__ = 'archive'
    __tablename__ = 'yasArchive'
    id = db.Column(db.Integer, primary_key=True)
    Path = db.Column(db.String, unique=True)
    LastSeen = db.Column(db.Integer, nullable=False) 
    Filename = db.Column(db.String, nullable=False) 
    Path = db.Column(db.String, nullable=False) 
    WriteTime = db.Column(db.Integer, nullable=False) 
    PatientName = db.Column(db.String, nullable=False) 
    PatientID = db.Column(db.String, nullable=False) 
    PatientAge = db.Column(db.String, nullable=False) 
    PatientGender = db.Column(db.String, nullable=False) 
    ProtocolName = db.Column(db.String, nullable=False) 
    AcquisitionTime = db.Column(db.String, nullable=False) 
    AcquisitionDate = db.Column(db.String, nullable=False) 
    MRSystem = db.Column(db.String, nullable=False) 
    AccessionNumber = db.Column(db.String, nullable=False) 
    YarraServer = db.Column(db.String, nullable=False) 

    def __repr__(self):
        return "<yas {} {}>".format(self.AccessionNumber, self.ProtocolName)

class AssetStatus(enum.Enum):
    up = 0
    down = 1
    unknown = 2

class User(db.Model,Base):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    roles = db.relationship('Role', secondary='user_roles')
    email = db.Column(db.String, nullable=False)

    @classmethod
    def get_id_field(self):
        return 'username'

    def get_id(self):
        return self.username

    def __repr__(self):
        return "<User {}>".format(self.username)

class SubmissionStatus(Enum):
     Pending = 1
     Submitting  = 2
     Submitted   = 3
     Failed   = 4

     def __str__(self):
        return self.name

class YarraTask(db.Model,Base):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='tasks')
    mode_id = db.Column(db.Integer, db.ForeignKey('mode_model.id'))
    mode = db.relationship('ModeModel')

    scan_file_path =    db.Column(db.String, nullable=False)
    protocol =          db.Column(db.String, nullable=False)
    patient_name =      db.Column(db.String, nullable=False)
    name =              db.Column(db.String, nullable=False)
    accession =         db.Column(db.String, nullable=True)
    priority =          db.Column(db.Enum(Priority))
    param_value =       db.Column(db.Integer)

    extra_files =       db.Column(db.PickleType, nullable=True)
    email_notifications=db.Column(db.PickleType, nullable=True)

    submission_status=  db.Column(db.Enum(SubmissionStatus), default=SubmissionStatus.Pending)
    created_date =      db.Column(UtcDateTime, default=utcnow())

class YarraServer(db.Model,Base):
    id =    db.Column(db.Integer, primary_key=True)
    path =  db.Column(db.String, nullable=False, default="", info={'label':'Path'})
    name =  db.Column(db.String, nullable=False, default="", info={'label':'Name'}, unique=True)
    modes = db.relationship('ModeModel', backref='server', lazy=True)
    roles = db.relationship('Role', secondary='server_roles')

    username =  db.Column(db.String, nullable=False, default="yarra", info={'label':'Path'})
    password =  db.Column(db.String, nullable=False, default="", info={'label':'Path'})

    def get_id(self):
        return self.name

    def __repr__(self):
        return "<Server {} ({}) {{{}}}>".format(self.name,self.path,",".join(map(str,self.roles)))

    @classmethod
    def get_id_field(self):
        return 'name'

    def connection(self):
        return ServerConnection(self.path,self.username, self.password)

    def update_modes(self):
        config = ConfigParser()
        config_file = io.BytesIO()

        with self.connection() as c:
            c.get('YarraModes.cfg',config_file)
        config.read_string(config_file.read().decode('UTF-8'))
        mode_info = ( (mode_entry[1], config[mode_entry[1]])  for mode_entry in config.items('Modes') )

        self.modes = [ModeModel(
                tag =                info.get('tag'),
                name =               name,
                desc =               info.get('name'),
                confirmation_mail =  info.get('confirmationmail'),
                requires_adj_scans = info.getboolean('requiresadjscans'),
                request_additional_files = info.getboolean('requestadditionalfiles'),
                requires_acc =       info.getboolean('requiresacc'),
                disabled =           info.getboolean('disabled'),
                required_server_type = info.get('requiredservertype'),
                sort_index =         info.getint('sortindex'),
                param_label =        info.get('paramlabel'),
                param_description =  info.get('paramdescription'),
                param_default =      info.getint('paramdefault'),
                param_min =          info.getint('parammin'),
                param_max =          info.getint('parammax')
            ) for name, info in mode_info
        ]


class ModeModel(db.Model,Base):
    id =            db.Column(db.Integer, primary_key=True)

    name =          db.Column(db.String,  nullable=False, info={'label':'asd'})
    desc =          db.Column(db.String,  nullable=False, info={'label':'Name'})
    sort_index =    db.Column(db.Integer, nullable=False, default=0) 
    requires_adj_scans = db.Column(db.Boolean, nullable=False, default=False) 
    requires_acc =  db.Column(db.Boolean, nullable=False, default=False) 
    confirmation_mail = db.Column(db.String,nullable=False,default="",info=dict(label='notification'))
    tag =           db.Column(db.String,  nullable=True) 
    required_server_type = db.Column(db.String,nullable=True) 
    server_id =     db.Column(db.Integer, db.ForeignKey('yarra_server.id'))

    param_label = db.Column(db.String)
    param_description = db.Column(db.String)
    param_default = db.Column(db.Integer)
    param_min = db.Column(db.Integer)
    param_max = db.Column(db.Integer)
    disabled = db.Column(db.Boolean, default=False)
    request_additional_files = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "<"+", ".join(map(str,[self.name,self.desc]))+ ( ' [{}]'.format(self.param_label) if self.param_label else "")+">"

# Define the UserRoles association table
class ServerRoles(db.Model,Base):
    __tablename__ = 'server_roles'
    id = db.Column(db.Integer(), primary_key=True)
    server_id = db.Column(db.Integer(), db.ForeignKey('yarra_server.id', ondelete='CASCADE'))
    role_id =   db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))



# Define the Role data-model
class Role(db.Model,Base):
    __tablename__ = 'roles'
    id =   db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    servers = db.relationship('YarraServer', secondary='server_roles')
    users = db.relationship('User', secondary='user_roles')

    def __repr__(self):
        return "<Role {}>".format(self.name)

    def get_id(self):
        return self.name

    @classmethod
    def get_id_field(self):
        return "name"

# Define the UserRoles association table
class UserRoles(db.Model,Base):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))
