#!/usr/bin/python3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash,send_from_directory
from flask_sqlalchemy import SQLAlchemy
#from datetime import datetime
from datetime import date


import flask_login
from extensions import db, login_manager, login_required

from yarrapyclient.yarraclient import Task

from models import User, Role, YarraServer, ModeModel

from sqlalchemy.sql import text
import resumable
import admin
import login_flow

import cli
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
   
    app.secret_key = "asdfasdfere"
    db.init_app(app) 
    login_manager.init_app(app)
    cli.init_app(app)
    app.register_blueprint(resumable.resumable_upload)
    app.register_blueprint(admin.admin)
    app.register_blueprint(login_flow.login_blueprint)

    return app

app = create_app()

@app.template_filter('dt')
def _jinja2_filter_datetime(date, fmt=None):
    if fmt:
        return date.strftime(fmt)
    else:
        return date.strftime('%m/%d/%Y %H:%M:%S')

@app.cli.command("submit")
def submit():
    server_name = '***REMOVED***'
    mode_name = 'MatlabSample'
    mode = db.session.query(ModeModel).join(ModeModel.server)\
                .filter(ModeModel.name==mode_name)\
                .filter(YarraServer.name==server_name).scalar()
    if mode is None:
        print("Invalid mode / server combination")
        return
    t = Task(mode, 'test.dat', 'theProtocol', 'John Doe', None)
    t.submit()
    print(t.task_data)
    print("OK")

@app.route('/')
@login_required('submitter')
def index():
    servers = db.session.query(YarraServer).from_statement(  # filtering servers by ones assigned to the same role as the user
        text("""SELECT yarra_server.* FROM yarra_server
             join server_roles on yarra_server.id = server_roles.server_id 
             join roles on server_roles.role_id = roles.id
             join user_roles on user_roles.role_id = roles.id 
             join user on user.id = user_roles.user_id 
             where user.id = :id
             """)).\
        params(id=flask_login.current_user.user.id).all()

    return render_template('submit.html', servers=servers)

@app.route("/submit_task", methods=['POST'])
@login_required('submitter')
def submit_task(): # todo: prevent submissions to incorrect servers
    print(request.form)
    mode = db.session.query(ModeModel).join(ModeModel.server)\
                .filter(ModeModel.name==request.form.get('mode'))\
                .filter(YarraServer.name==request.form.get('server')).scalar()
    if not mode:
        return abort(400)
    t = Task(mode, '/tmp/'+request.form.get('file'),
         request.form.get('protocol'), 
         request.form.get('accession',None),
         request.form.get('patient_name'))
    print("submitting")
    t.submit()
    print("done")
    return redirect("/")

if __name__ == "__main__":
    app.run()
