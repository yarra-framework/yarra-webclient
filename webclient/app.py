#!/usr/bin/python3
import re
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash,send_from_directory, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_jsontools import DynamicJSONEncoder

from datetime import date, timezone, datetime
import os, cli, traceback
import click, flask_login

from extensions import db, login_manager, login_required, json_errors, make_celery
from models import User, Role, YarraServer, ModeModel, yasArchive, YarraTask, SubmissionStatus
from yarrapyclient.yarraclient import Task, Priority

from sqlalchemy.sql import text
from resumable import resumable_upload as upload_blueprint
from admin import admin as admin_blueprint
from login_flow import login_blueprint
from sqlalchemy.orm.session import make_transient

def create_app():
    global celery
    app = Flask(__name__, static_url_path='', static_folder='files')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/data.sqlite'
    app.config['SQLALCHEMY_BINDS']  = {
        'archive':        'sqlite:///data/yas.db',
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['YARRA_UPLOAD_BASE_DIR'] = '/tmp'

    app.config['YARRA_ARCHIVE_UPLOAD'] = os.environ.get("YARRA_ARCHIVE_UPLOAD", 'False').lower() == 'true'

    app.secret_key = os.environ.get("YARRA_SECRET_KEY")
    db.init_app(app) 
    try: 
        db.create_all()
    except:
        pass
    login_manager.init_app(app)
    cli.init_app(app)
    app.register_blueprint(upload_blueprint)
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(login_blueprint)
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.json_encoder = DynamicJSONEncoder
    celery = make_celery(app)
    return app

app = create_app()

@app.template_filter('dt')
def _jinja2_filter_datetime(date, fmt=None):
    if fmt:
        return date.astimezone(tz=None).strftime(fmt)
    else:
        return date.astimezone(tz=None).strftime('%m/%d/%Y %H:%M:%S %Z')


@app.template_filter('active_eq')
def active_if(a, eq):
    if a == eq:
        return "active"
    return ""

@app.template_filter('each')
def each(a):
    return [x.__dict__ for x in a]


@app.route('/batch_search')
@login_required('submitter')
def batch_search():
    needle = request.args.get('needle')
    offset = int(request.args.get('offset') or 0)
    if not needle: return jsonify({"records": []})

    accessions = re.split(",| |\n", needle)
    accessions = [x for x in accessions if len(x)]
    print(accessions)
    e = (db.session
        .query(yasArchive)
        .filter((yasArchive.AccessionNumber.in_(accessions))
                ).order_by(yasArchive.WriteTime.desc()).all())
    accessions_found = set(x.AccessionNumber for x in e)
    accessions_missing = set(accessions).difference(accessions_found)

    return jsonify({"records":[dict(
                id = e.id,
                accession = e.AccessionNumber,
                patient_name = e.PatientName,
                filename = e.Filename,
                patient_id = e.PatientID,
                acquisition_time = e.AcquisitionTime,
                acquisition_date = e.AcquisitionDate,
                protocol = e.ProtocolName,) for e in e],
                "accessions_missing": list(accessions_missing)
            })

@app.route('/search')
@login_required('submitter')
def search():
    needle = request.args.get('needle')
    offset = int(request.args.get('offset') or 0)
    if not needle: return jsonify({"records":[]})
    if needle.find("+")==-1:
        e = db.session.query(yasArchive).filter((yasArchive.AccessionNumber == needle) |
                                                 yasArchive.PatientName.ilike("%{}%".format(needle)) |
                                                 yasArchive.Filename.ilike("%{}%".format(needle)) |
                                                 yasArchive.ProtocolName.ilike("%{}%".format(needle)) |
                                                 (yasArchive.PatientID == needle)
                                                 ).order_by(yasArchive.WriteTime.desc()).offset(offset).limit(request.args.get('limit', 20)).all()
    else:
        needles = [n.strip() for n in needle.split("+")]
        e = db.session.query(yasArchive).from_statement(
            text("""SELECT yasArchive.* FROM yasArchive
                where {}
                  order by WriteTime desc
                  limit 20 offset :offset
                  """.format(
                    " and ".join(["""(
                        PatientName like '%'||:needle{} ||'%' COLLATE NOCASE OR
                        ProtocolName like '%'||:needle{} ||'%' COLLATE NOCASE OR
                        Filename like '%'||:needle{} ||'%' COLLATE NOCASE OR
                        PatientID = :needle{} COLLATE NOCASE OR
                        )""".format(i,i,i) for i in range(len(needles))])
                    ))).\
                params({'offset':offset,**{'needle{}'.format(i):needles[i] for i in range(len(needles))}}).all()


    result = jsonify({"records": [dict(id = e.id,
                           accession = e.AccessionNumber,
                           patient_name = e.PatientName,
                           filename = e.Filename,
                           patient_id = e.PatientID,
                           acquisition_time = e.AcquisitionTime,
                           acquisition_date = e.AcquisitionDate,
                           protocol = e.ProtocolName,) for e in e]})
    return result

@app.cli.command("test")
@click.argument('acc')
def test(acc):
    # def task(self,mode,task_id, priority=):
    #     return 
    e = db.session.query(yasArchive).filter(yasArchive.AccessionNumber == acc).scalar()
    file_path = os.path.join(e.Path.replace('V:/Archive/','/media/archive/'), e.Filename)
    # server_name = '***REMOVED***'
    # mode_name = 'MatlabSample'
    # mode = db.session.query(ModeModel).join(ModeModel.server)\
    #             .filter(ModeModel.name==mode_name)\
    #             .filter(YarraServer.name==server_name).scalar()

    # task = Task(mode, os.path.join(e.Path,e.Filename), e.ProtocolName, e.PatientName, 'test', None, Priority.Normal)
    # print(os.path.join(e.Path,e.Filename))
    # print(task.task_data.to_config())
    # task.submit()


@celery.task
def update_server_modes():
    for s in db.session.query(YarraServer).all():
        s.update_modes()
    db.session.commit()

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60.0*60.0, update_server_modes.s(), name='update server modes')

@app.cli.command("test_celery")
def test():
    test_task.delay()

@celery.task
def background_submit(task_id):
    yarra_task = db.session.query(YarraTask).get(task_id)
    print("Submitting", yarra_task)
    try:
        t = Task.from_other(yarra_task)
        print("Details:", t)
        yarra_task.submission_status = SubmissionStatus.Submitting
        db.session.commit()
        t.submit()
        yarra_task.submission_status = SubmissionStatus.Submitted
        db.session.commit()
    except Exception as e:
        traceback.print_exc()
        yarra_task.submission_status = SubmissionStatus.Failed
    finally:
        db.session.commit()



@app.cli.command("resubmit")
@click.argument('task_id')
@click.argument('mode')
@click.argument('server_name')
@click.argument('priority',default='')
def resubmit(task_id,mode,server_name,priority):
    if (priority == 'high'):
        priority = Priority.High 
    elif (priority == 'night'):
        priority = Priority.Night 
    else:
        priority = Priority.Normal

    task = db.session.query(YarraTask).get(task_id)
    db.session.expunge(task)
    make_transient(task)
    task._oid = None
    task.id = None
    task.mode = db.session.query(ModeModel).join(ModeModel.server)\
                 .filter(ModeModel.name==mode)\
                 .filter(YarraServer.name==server_name).scalar()
    print("mode", task.mode)
    db.session.add(task)
    db.session.commit()
    background_submit.delay(task.id)
    print("OK")

@app.cli.command("submit")
@click.argument('task_id')
@click.argument('priority',default='')
def submit(task_id,priority):
    server_name = '***REMOVED***'
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
    yarra_task = YarraTask(user_id=1,mode=mode, scan_file_path='test.dat', protocol='theProtocol', patient_name='John Doe',name=task_id,accession=None, priority=priority,extra_files=['extra1.dat','extra2.dat'])
    db.session.add(yarra_task)
    db.session.commit()
    background_submit.delay(yarra_task.id)

    # t = Task.from_other(yarra_task)
    #t = Task(mode, 'test.dat', 'theProtocol', 'John Doe', task_id, None, priority, ['extra1.dat','extra2.dat'])

    # background_submit.delay(mode_name,server_name, 'test.dat', 'theProtocol', 'John Doe', task_id, None, priority, ['extra1.dat','extra2.dat'])
    # t.submit()
    # print(t.task_data.to_config())
    print("OK")

@app.route('/files/submit.js')
def submit_js():
    return send_from_directory('.',
                               'files/submit.js')
@app.route('/files/iecheck.js')
def iecheck():
    return send_from_directory('.',
                               'files/iecheck.js')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('.',
                               'files/favicon.ico')

@app.route('/tasks')
@app.route('/tasks/<status>')
@login_required()
def tasks(status='pending'):
    tasks = flask_login.current_user.user.tasks
    if status == 'pending':
        tasks = [ t for t in tasks if t.submission_status in (SubmissionStatus.Submitting, SubmissionStatus.Pending)  ]
    else:
        tasks = [ t for t in tasks if t.submission_status==SubmissionStatus[status.title()] ]

    tasks.sort(key=lambda x:x.id, reverse=True)
    return render_template('tasks.html', tasks=tasks, status=status)



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

    servers_dict = { s.name: {m.name:m for m in s.modes} for s in servers}
    print(servers_dict)
    return render_template('submit.html', servers=servers, servers_dict = servers_dict)

@app.route("/submit_tasks", methods=['POST'])
@login_required('submitter')
@json_errors()
def submit_tasks():
    task_n = len(request.form.getlist("taskid"))

    form_keys = ("protocol", "patient_name", "taskid", "accession")

    lists = {x:request.form.getlist(x) for x in form_keys}

    for l in lists.values():
        if len(l) != task_n:
            return abort(400, "Invalid request: mismatched lists")
    
    mode = db.session.query(ModeModel).join(ModeModel.server)\
            .filter(ModeModel.name==request.form.get('mode'))\
            .filter(YarraServer.name==request.form.get('server')).scalar()
    
    if not mode:
        return abort(400, "Invalid mode")

    if request.form.get('archive_id'):
        if not app.config['YARRA_ARCHIVE_UPLOAD']:
            return abort(400, "Invalid")
        archive_object = db.session.query(yasArchive).filter(yasArchive.id == request.form.get('archive_id')).scalar()
        path = os.path.join(archive_object.Path.replace('V:/Archive/','/archive/'))
        filepath = os.path.join(path, archive_object.Filename)
    else:
        if not request.form.get('file'):
            return abort(400, "'file' parameter missing")
        filepath = os.path.join(app.config['YARRA_UPLOAD_BASE_DIR'], flask_login.current_user.id, request.form.get('file'))

    processing = request.form.get('processing').lower()
    priority = Priority.Normal
    if processing == 'night':
        priority = Priority.Night
    elif processing == 'priority':
        priority = Priority.High

    tasks = []
    for n in range(task_n):
        yarra_task = YarraTask(
                    user =         flask_login.current_user.user,
                    mode =         mode,
                    scan_file_path=filepath, 
                    protocol =     lists["protocol"][n],
                    patient_name = lists["patient_name"][n],
                    name =         lists["taskid"][n]+datetime.now().strftime("_%Y%m%d_%H%M%S_%f"),
                    accession =    lists["accession"][n],
                    param_value =  request.form.get('param'),
                    priority =     priority,
                    extra_files =  []
                    )
        print(yarra_task)
        test_t = Task.from_other(yarra_task) # will throw if this is an invalid task
        tasks.append(yarra_task)
    
    for t in tasks:
        db.session.add(t)
        db.session.commit()

    print("submitting")
    for t in tasks:
        background_submit.delay(t.id)
    flash(f"{task_n} tasks are being submitted.","success")

    return "OK"

if __name__ == "__main__":
    app.run()
