from extensions import db, login_manager, login_required, json_errors 
from flask import Blueprint, render_template, abort
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash,send_from_directory
from flask import current_app
import os
import flask_login

resumable_upload = Blueprint('resumable_upload', __name__,
                        template_folder='templates')

@resumable_upload.route('/files/resumable.js')
def js():
    return send_from_directory('.',
                               'files/resumable.js')

# resumable.js uses a GET request to check if it uploaded the file already.
# NOTE: your validation here needs to match whatever you do in the POST (otherwise it will NEVER find the files)
@resumable_upload.route("/resumable_upload", methods=['GET'])
@login_required('submitter')
@json_errors()
def resumable():
    resumableIdentifier = request.args.get('resumableIdentifier', type=str)
    resumableFilename = request.args.get('resumableFilename', type=str)
    resumableChunkNumber = request.args.get('resumableChunkNumber', type=int)

    if not resumableIdentifier or not resumableFilename or not resumableChunkNumber:
        # Parameters are missing or invalid
        abort(500, 'Parameter error')

    temp_base = current_app.config['YARRA_UPLOAD_BASE_DIR']
    # chunk folder path based on the parameters
    temp_dir = os.path.join(temp_base, flask_login.current_user.id, resumableIdentifier)

    # chunk path based on the parameters
    chunk_file = os.path.join(temp_dir, get_chunk_name(resumableFilename, resumableChunkNumber))
    current_app.logger.debug('Getting chunk: %s', chunk_file)

    if os.path.isfile(chunk_file):
        # Let resumable.js know this chunk already exists
        return 'OK'
    else:
        # Let resumable.js know this chunk does not exists and needs to be uploaded
        abort(404, 'Not found')


# if it didn't already upload, resumable.js sends the file here
@resumable_upload.route("/resumable_upload", methods=['POST'])
@login_required('submitter')
@json_errors()
def resumable_post():
    resumableTotalChunks = request.form.get('resumableTotalChunks', type=int)
    resumableChunkNumber = request.form.get('resumableChunkNumber', default=1, type=int)
    resumableFilename =    request.form.get('resumableFilename', default='error', type=str)
    resumableIdentifier =  request.form.get('resumableIdentifier', default='error', type=str)

    # get the chunk data
    chunk_data = request.files['file']

    # make our temp directory
    temp_base = current_app.config['YARRA_UPLOAD_BASE_DIR']
    temp_dir = os.path.join(temp_base, flask_login.current_user.id, resumableIdentifier)
    if not os.path.isdir(temp_dir):
        os.makedirs(temp_dir)

    # save the chunk data
    chunk_name = get_chunk_name(resumableFilename, resumableChunkNumber)
    chunk_file = os.path.join(temp_dir, chunk_name)
    chunk_data.save(chunk_file)
    current_app.logger.debug('Saved chunk: %s', chunk_file)

    # check if the upload is complete
    chunk_paths = [os.path.join(temp_dir, get_chunk_name(resumableFilename, x)) for x in range(1, resumableTotalChunks+1)]
    upload_complete = all([os.path.exists(p) for p in chunk_paths])

    # combine all the chunks to create the final file
    if upload_complete:
        target_file_name = os.path.join(temp_base,flask_login.current_user.id, resumableFilename)
        with open(target_file_name, "ab") as target_file:
            for p in chunk_paths:
                stored_chunk_file_name = p
                stored_chunk_file = open(stored_chunk_file_name, 'rb')
                target_file.write(stored_chunk_file.read())
                stored_chunk_file.close()
                os.unlink(stored_chunk_file_name)
        target_file.close()
        os.rmdir(temp_dir)
        current_app.logger.debug('File saved to: %s', target_file_name)

    return 'OK'

def get_chunk_name(uploaded_filename, chunk_number):
    return uploaded_filename + "_part_%03d" % chunk_number

