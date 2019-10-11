#!/usr/bin/python3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import date

import click
import flask_login
from extensions import db, login_manager, login_required, json_errors

from yarrapyclient.yarraclient import Task, Priority

from models import User, Role, YarraServer, ModeModel

from sqlalchemy.sql import text
import resumable
import admin
import login_flow
import os
import cli

def create_app():
    app = Flask(__name__, static_url_path='', static_folder='files')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['YARRA_UPLOAD_BASE_DIR'] = 'tmp'
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
@click.argument('task_id')
@click.argument('priority',default='')
def submit(task_id,priority):
    server_name = 'YarraAda'
    mode_name = 'MatlabSample'
    if (priority == 'high'):
        priority = Priority.High 
    elif (priority == 'night'):
        priority = Priority.Night 
    else:
        priority = Priority.Normal

    mode = db.session.query(ModeModel).join(ModeModel.server)\
                .filter(ModeModel.name==mode_name)\
                .filter(YarraServer.name==server_name).scalar()
    if mode is None:
        print("Invalid mode / server combination")
        return
    t = Task(mode, 'test.dat', 'theProtocol', 'John Doe', task_id, None, priority, ['extra1.dat','extra2.dat'])
    t.submit()
    print(t.task_data.to_config())
    print("OK")

@app.route('/files/submit.js')
def submit_js():
    return send_from_directory('.',
                               'files/submit.js')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('.',
                               'files/favicon.ico')


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
@json_errors()
def submit_task(): # todo: prevent submissions to incorrect servers
    print(request.form)
    extra_files = request.form.getlist('extra_files')
    for k in ['file','mode','server','protocol','patient_name','taskid', 'processing']:
        if not request.form.get(k):
            return abort(400, "Missing field: '{}' is empty.".format(k))

    mode = db.session.query(ModeModel).join(ModeModel.server)\
                .filter(ModeModel.name==request.form.get('mode'))\
                .filter(YarraServer.name==request.form.get('server')).scalar()

    if not mode:
        return abort(400, "Invalid mode")

    processing = request.form.get('processing').lower()
    priority = Priority.Normal
    if processing == 'night':
        priority = Priority.Night
    elif processing == 'priority':
        priority = Priority.High
    t = Task(mode, os.path.join(app.config['YARRA_UPLOAD_BASE_DIR'], flask_login.current_user.id, request.form.get('file')),
         request.form.get('protocol'), 
         request.form.get('patient_name'),
         request.form.get('taskid'),
         request.form.get('accession',None),
         priority,
         [os.path.join(app.config['YARRA_UPLOAD_BASE_DIR'], flask_login.current_user.id, f) for f in extra_files if f]
         )
    print("submitting")
    t.submit()
    print("done")
    return "OK"
if __name__ == "__main__":
    app.run()
