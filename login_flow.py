from models import User
from forms import LoginForm
from app import login_manager
from app import app
from app import pwd_context
import flask_login
from flask import flash, redirect, url_for, request, render_template
class LoginUser(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    user = User.query.filter_by(username=username).one_or_none()
    if not user:
        return
    login_user = LoginUser()
    login_user.id = user.username
    return login_user


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).one_or_none()
    if not user:
        return
    login_user = LoginUser()
    login_user.id = user.username
    user.is_authenticated = pwd_context.verify(request.form['password'], user.password)
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    next = request.args.get('next')
    form = LoginForm()
    if request.method == 'GET':
        return render_template('login.html',form=form)
    username = form.username.data
    user = User.query.filter_by(username=username).one_or_none()
    if user and pwd_context.verify(form.password.data, user.password):
        login_user = LoginUser()
        login_user.id = username
        flask_login.login_user(login_user)
        return redirect(next or url_for('user_edit'))

    flash('Bad login','danger')
    return redirect(request.referrer)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    flash("Logged out","success")
    return redirect(url_for('login'))

@login_manager.unauthorized_handler
def unauthorized():
    flash("Login required",'warning')
    return redirect(url_for('login',next=request.path))