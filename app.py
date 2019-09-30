#!/usr/bin/python3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random, string, enum
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired,Length
from datetime import date
from flask.views import View

import flask_login
from flask_login import LoginManager
from passlib.apps import custom_app_context as pwd_context
from extensions import db, login_manager

from yarrapyclient.yarraclient import *

from models import User, Role, InstructionTemplate, StatusEvent,Asset, AssetStatus
from forms import NewForm, LoginForm, AssetReportForm, InstructionTemplateForm, AssetEditForm
from functools import wraps
import click
from flask.cli import AppGroup
from getpass import getpass

admin_views = []


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite'
    app.secret_key = "asdfasdfere"
    db.init_app(app) 
    login_manager.init_app(app)
    return app

app = create_app()
import login_flow

def login_required(role=None):
    def decorator(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not flask_login.current_user.is_authenticated:
                return login_manager.unauthorized()

            if ( role is not None and role not in flask_login.current_user.roles):
                flash("insufficient permissions",'warning')
                if (request.path != "/"):
                    return redirect("/") 
                else: 
                    return redirect(url_for("login")) 

            return fn(*args, **kwargs)
        return decorated_view
    return decorator



temp_base = '/tmp'

@app.route('/files/resumable.js')
def js():
    return send_from_directory('.',
                               'files/resumable.js')



@app.template_filter('dt')
def _jinja2_filter_datetime(date, fmt=None):
    if fmt:
        return date.strftime(fmt)
    else:
        return date.strftime('%m/%d/%Y %H:%M:%S')


user_cli = AppGroup('user')

@user_cli.command('create')
@click.argument('name')
def create_user(name):
    roles = [db.session.query(Role).filter_by(name=r).scalar() for r in ['admin','submitter']]
    pw = getpass()
    new_user =  User(username=name, password=pwd_context.hash(pw),roles=roles)
    db.session.add(new_user)
    db.session.commit()
    print("Done")

@user_cli.command('list')
def list_users():
    users = db.session.query(User).all()
    for u in users:
        print(u, ", ".join([role.name for role in u.roles]))

@user_cli.command('reset')
@click.argument('name')
def reset_pw(name):
    user = db.session.query(User).filter_by(username=name).first()
    user.password = pwd_context.hash(getpass())
    db.session.commit()


app.cli.add_command(user_cli)

@app.cli.command("reset")
def reset():
    if input("Really reset the entire database? (Y/N) ") != "Y":
        return
    db.drop_all()
    db.create_all()
    admin_role = Role(name="admin")
    db.session.add(admin_role)
    submit_role = Role(name="submitter")
    db.session.add(submit_role)
    test_user = User(username="roy", password=pwd_context.hash("roy"),roles=[admin_role,submit_role])
    db.session.add(test_user)
    db.session.commit()
    print("OK")

@app.route('/admin/')
@login_required()
def admin_page():
    return redirect(url_for("user_edit"))

servers = [Server('***REMOVED***','***REMOVED***'), 
            Server('***REMOVED***','***REMOVED***')]

@app.route('/')
@login_required('submitter')
def index():
    return render_template('submit.html', servers=servers)

@app.route("/submit_task", methods=['POST'])
@login_required('submitter')
def submit_task():
    print(request.form)
    for s in servers:
      if s.name == request.form.get('server'):
        server = s
    if not server:
        return abort(400)
    t = Task(server, request.form.get('mode'), '/tmp/'+request.form.get('file'),
         request.form.get('protocol'), 
         request.form.get('accession',None),
         request.form.get('patient_name'))
    print("submitting")
    t.submit()
    print("done")
    return redirect("/")

# resumable.js uses a GET request to check if it uploaded the file already.
# NOTE: your validation here needs to match whatever you do in the POST (otherwise it will NEVER find the files)
@app.route("/resumable_upload", methods=['GET'])
@login_required('submitter')
def resumable():
    resumableIdentifier = request.args.get('resumableIdentifier', type=str)
    resumableFilename = request.args.get('resumableFilename', type=str)
    resumableChunkNumber = request.args.get('resumableChunkNumber', type=int)

    if not resumableIdentifier or not resumableFilename or not resumableChunkNumber:
        # Parameters are missing or invalid
        abort(500, 'Parameter error')

    # chunk folder path based on the parameters
    temp_dir = os.path.join(temp_base, resumableIdentifier)

    # chunk path based on the parameters
    chunk_file = os.path.join(temp_dir, get_chunk_name(resumableFilename, resumableChunkNumber))
    app.logger.debug('Getting chunk: %s', chunk_file)

    if os.path.isfile(chunk_file):
        # Let resumable.js know this chunk already exists
        return 'OK'
    else:
        # Let resumable.js know this chunk does not exists and needs to be uploaded
        abort(404, 'Not found')


# if it didn't already upload, resumable.js sends the file here
@app.route("/resumable_upload", methods=['POST'])
@login_required('submitter')
def resumable_post():
    resumableTotalChunks = request.form.get('resumableTotalChunks', type=int)
    resumableChunkNumber = request.form.get('resumableChunkNumber', default=1, type=int)
    resumableFilename = request.form.get('resumableFilename', default='error', type=str)
    resumableIdentifier = request.form.get('resumableIdentifier', default='error', type=str)

    # get the chunk data
    chunk_data = request.files['file']

    # make our temp directory
    temp_dir = os.path.join(temp_base, resumableIdentifier)
    if not os.path.isdir(temp_dir):
        os.makedirs(temp_dir)

    # save the chunk data
    chunk_name = get_chunk_name(resumableFilename, resumableChunkNumber)
    chunk_file = os.path.join(temp_dir, chunk_name)
    chunk_data.save(chunk_file)
    app.logger.debug('Saved chunk: %s', chunk_file)

    # check if the upload is complete
    chunk_paths = [os.path.join(temp_dir, get_chunk_name(resumableFilename, x)) for x in range(1, resumableTotalChunks+1)]
    upload_complete = all([os.path.exists(p) for p in chunk_paths])

    # combine all the chunks to create the final file
    if upload_complete:
        target_file_name = os.path.join(temp_base, resumableFilename)
        with open(target_file_name, "ab") as target_file:
            for p in chunk_paths:
                stored_chunk_file_name = p
                stored_chunk_file = open(stored_chunk_file_name, 'rb')
                target_file.write(stored_chunk_file.read())
                stored_chunk_file.close()
                os.unlink(stored_chunk_file_name)
        target_file.close()
        os.rmdir(temp_dir)
        app.logger.debug('File saved to: %s', target_file_name)

    return 'OK'


def get_chunk_name(uploaded_filename, chunk_number):
    return uploaded_filename + "_part_%03d" % chunk_number



class ObjectView(View):
    def __init__(self, asset_model,view_func):
        self.Model = asset_model
        self.Form = self.Model.form
        self.view_func = view_func

    def dispatch_request(self,identifier,method):
        assets = self.Model.query.all()

        if method == 'new':
            asset = self.Model()
        elif not identifier:
            return redirect(url_for(self.view_func,identifier=assets[0].get_id(), method=method))
        else:
            asset = self.Model.query.filter_by(**{self.Model.get_id_field():identifier}).first()
        form = self.Form(obj=asset)

        if request.method == 'POST':
            if method == 'delete': #todo: csrf
                db.session.delete(asset)
                db.session.commit()
                flash("Deleted.","primary")
                return redirect(url_for(self.view_func,method='edit'))

            if form.validate_on_submit():
                form.populate_obj(asset)
                if method == 'new':
                    db.session.add(asset)
                    db.session.commit()
                    flash("Created","primary")
                    return redirect(url_for(self.view_func,method='edit'))

                db.session.commit()
                flash('Submitted.','primary')
                return redirect(request.referrer)
        return render_template('asset-edit.html',admin_views=admin_views,asset=asset,assets=assets,form=form,new_form=NewForm(),view_func=self.view_func)

def register_view( model, path, view_name):
	admin_views.append(dict(view_name=view_name,name=model.__name__))
	view = ObjectView.as_view(view_name, model,view_name)
	view = login_required('admin')(view)

	app.add_url_rule('/admin/{}/'.format(path), view_func=view, defaults={'method':'edit','identifier': None})
	app.add_url_rule('/admin/{}/<method>/'.format(path),view_func=view,defaults={'identifier': None}, methods=['GET','POST'])
	app.add_url_rule('/admin/{}/<method>/<identifier>'.format(path),view_func=view,methods=['GET','POST'])

register_view(User,'user','user_edit')

if __name__ == "__main__":
    app.run()
