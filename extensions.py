from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from functools import wraps
from flask import flash, request, redirect,jsonify, make_response
import flask_login
from flask_login import LoginManager
from passlib.apps import custom_app_context as pwd_context

db = SQLAlchemy()
login_manager = LoginManager()
from werkzeug.exceptions import HTTPException
import traceback

from flask import json

from celery import Celery

def make_celery(app):
    celery = Celery('app')#, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update({
        'broker_url': 'filesystem://',
        'broker_transport_options': {
            'data_folder_in': 'broker/out',
            'data_folder_out': 'broker/out',
            'data_folder_processed': 'broker/processed'
        },
        # 'imports': ('tasks',),
        'result_persistent': False,
        'task_serializer': 'json',
        'result_serializer': 'json',
        'accept_content': ['json']})

    # celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

# from celery import Celery

# celery = Celery('app')
# celery.conf.update({
#     'broker_url': 'filesystem://',
#     'broker_transport_options': {
#         'data_folder_in': 'broker/out',
#         'data_folder_out': 'broker/out',
#         'data_folder_processed': 'broker/processed'
#     },
#     # 'imports': ('tasks',),
#     'result_persistent': False,
#     'task_serializer': 'pickle',
#     'result_serializer': 'json',
#     'accept_content': ['pickle']})


def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

def json_errors():
    def decorator(fn):
        @wraps(fn)
        def decorated(*args,**kwargs):
            try:
                return fn(*args,**kwargs)
            except HTTPException as e:
                traceback.print_exc()
                return handle_exception(e)
            except Exception as e:
                traceback.print_exc()
                r = make_response(jsonify(dict(code=500,name="",description=str(e))),500)
                r.content_type = "application/json"
                return r

        return decorated
    return decorator


def login_required(role=None):
    def decorator(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not flask_login.current_user.is_authenticated:
                return login_manager.unauthorized()

            if ( role is not None and role not in flask_login.current_user.roles):
                flash("Insufficient permissions",'warning')
                if (request.path != "/"):
                    return redirect("/") 
                else: 
                    return redirect(url_for("login")) 

            return fn(*args, **kwargs)
        return decorated_view
    return decorator

