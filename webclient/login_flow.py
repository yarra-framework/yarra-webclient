from models import User
from forms import LoginForm, RegisterForm, PasswordChangeForm
from extensions import login_manager
from extensions import pwd_context
from extensions import db

import flask_login
from flask import flash, redirect, url_for, request, render_template, Blueprint

login_blueprint = Blueprint('login', __name__,
                        template_folder='templates')

class LoginUser(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    user = User.query.filter_by(username=username).one_or_none()
    if not user:
        return
    login_user = LoginUser()
    login_user.roles = [x.name for x in user.roles]
    login_user.id = user.username
    login_user.email = user.email
    login_user.user = user
    for role in user.roles:
        if role.name == 'admin':
            login_user.is_admin = True

    return login_user


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).one_or_none()
    if not user:
        return
    login_user = LoginUser()
    login_user.roles = [x.name for x in user.roles]
    login_user.id = user.username
    login_user.email = user.email
    login_user.user = user
    user.is_authenticated = pwd_context.verify(request.form['password'], user.password)
    return user

@login_blueprint.route('/password_change', methods=['GET', 'POST'])
def password_change():
    if not flask_login.current_user.is_authenticated:
        return redirect('/')
    form = PasswordChangeForm()
    if request.method == 'POST' and form.validate():
        flask_login.current_user.user.password = pwd_context.hash(form.password.data)
        db.session.commit()
        flash('Password updated')
        return redirect('/')
    return render_template('login.html',form=form)


@login_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if flask_login.current_user.is_authenticated:
        return redirect('/')
    form = RegisterForm()
    if request.method == 'POST' and form.validate():
        user = User(username = form.username.data, password = pwd_context.hash(form.password.data))
        db.session.add(user)
        db.session.commit()
        flash('Registration recieved')
        return redirect(url_for('login.login'))
    return render_template('login.html',form=form)
    # return redirect(request.referrer)

@login_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        if flask_login.current_user.is_authenticated:
            return redirect('/')
        return render_template('login.html',form=form)

    next = request.args.get('next')
    username = form.username.data
    user = User.query.filter_by(username=username).one_or_none()
    if user and pwd_context.verify(form.password.data, user.password):
        login_user = LoginUser()
        login_user.id = username
        flask_login.login_user(login_user)
        return redirect(next or url_for('admin.user_edit'))

    flash('Bad login','danger')
    return redirect(request.referrer)

@login_blueprint.route('/logout')
def logout():
    flask_login.logout_user()
    flash("Logged out","success")
    return redirect(url_for('login.login'))

@login_manager.unauthorized_handler
def unauthorized(**kwargs):
    flash("Login required",'warning')
    return redirect(url_for('login.login',next=request.path))