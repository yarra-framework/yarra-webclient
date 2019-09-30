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


from yarrapyclient.yarraclient import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite'
db = SQLAlchemy(app)
app.secret_key = "asdfasdfere"

temp_base = '/tmp'

@app.route('/files/resumable.js')
def js():
    print("resumable")
    return send_from_directory('.',
                               'files/resumable.js')
login_manager = LoginManager()
login_manager.init_app(app)

from models import User, Role, InstructionTemplate, StatusEvent,Asset, AssetStatus
from forms import NewForm, LoginForm, AssetReportForm, InstructionTemplateForm, AssetEditForm
import login_flow

admin_views = []


@app.template_filter('dt')
def _jinja2_filter_datetime(date, fmt=None):
    if fmt:
        return date.strftime(fmt)
    else:
        return date.strftime('%m/%d/%Y %H:%M:%S')


@app.route("/reset")
def reset():
    db.drop_all()
    db.create_all()
#    test_instructions = InstructionTemplate(name="default",text="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam fringilla est in porttitor varius. Vestibulum ligula quam, viverra at tincidunt eget, ornare eget nisl. Praesent ac mollis diam. Etiam neque turpis, dictum sit amet consectetur quis, sollicitudin nec lacus. Nullam in tortor commodo, facilisis felis sed, molestie tortor. Cras lacinia, lectus ac ultrices consequat, diam orci auctor erat, in vestibulum risus odio vel urna. Donec elit lacus, rutrum sed bibendum consequat, tincidunt sed dolor. Cras accumsan iaculis arcu, vitae congue ligula ultricies a. Proin placerat massa commodo commodo dignissim. Phasellus id tellus varius, finibus erat eget, consectetur tortor. Aliquam pretium justo ut tincidunt porttitor. Quisque non risus posuere, facilisis nibh id, bibendum tellus. Suspendisse potenti. Fusce a dolor id lectus malesuada convallis. Nullam euismod, quam in sodales faucibus, massa augue facilisis quam, eget mollis neque urna et neque. Nulla facilisi. Nam semper tempus dolor eu cursus. Integer nec tristique enim.""")
#    test_asset = Asset(name="Skyra", building="CBI",type="MR",shortcode="0YFWLY3",instruction_template = test_instructions)
#    test_asset = Asset(name="Aera", building="CBI",type="MR",shortcode="FTC3W34",instruction_template = test_instructions)
#    db.session.add(test_asset)
    admin_role = Role(name="Admin")
    db.session.add(admin_role)
    submit_role = Role(name="Submitter")
    db.session.add(submit_role)
    test_user = User(username="roy", password=pwd_context.hash("roy"),roles=[admin_role,submit_role])
    db.session.add(test_user)
    db.session.commit()
    return "OK"

@app.route('/admin/')
@flask_login.login_required
def admin_page():
    return redirect(url_for("user_edit"))

servers = [Server('AGR1','xdglpdcdap001.nyumc.org'), 
            Server('YarraAda','xdglpdcdap002.nyumc.org')]

@app.route('/')
@flask_login.login_required
def index():
    print(servers[0].modes)
    return render_template('submit.html', servers=servers)

@app.route("/submit_task", methods=['POST'])
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
	view = flask_login.login_required(view)
	app.add_url_rule('/admin/{}/'.format(path), view_func=view, defaults={'method':'edit','identifier': None})
	app.add_url_rule('/admin/{}/<method>/'.format(path),view_func=view,defaults={'identifier': None}, methods=['GET','POST'])
	app.add_url_rule('/admin/{}/<method>/<identifier>'.format(path),view_func=view,methods=['GET','POST'])

#register_view(Asset,'asset','asset_edit')
#register_view(InstructionTemplate,'template','template_edit')
register_view(User,'user','user_edit')

if __name__ == "__main__":
    app.run()
