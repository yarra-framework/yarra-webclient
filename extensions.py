from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from functools import wraps
from flask import flash, request, redirect
import flask_login
from flask_login import LoginManager
from passlib.apps import custom_app_context as pwd_context

db = SQLAlchemy()
login_manager = LoginManager()


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

