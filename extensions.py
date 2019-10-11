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

