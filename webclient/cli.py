from flask.cli import AppGroup
from extensions import db, pwd_context
from models import User, Role, YarraServer, ModeModel, YarraTask
import click
from getpass import getpass

user_cli = AppGroup('user')
server_cli = AppGroup('server')
db_cli = AppGroup('db')

@user_cli.command('create')
@click.argument('name')
@click.argument('email')
def create_user(name,email):
    roles = [db.session.query(Role).filter_by(name=r).scalar() for r in ['admin','submitter']]
    pw = getpass()
    new_user =  User(username=name, email=email, password=pwd_context.hash(pw),roles=roles)
    db.session.add(new_user)
    db.session.commit()
    print("Done")

@user_cli.command('list')
def list_users():
    users = db.session.query(User).all()
    for u in users:
        print(u, ", ".join([role.name for role in u.roles]))



@user_cli.command('tasks')
@click.argument('user')
def list_users(user):
    tasks = db.session.query(YarraTask).join(User).filter(User.username == user)
    for t in tasks:
        print(t)


@user_cli.command('reset')
@click.argument('name')
def reset_pw(name):
    user = db.session.query(User).filter_by(username=name).first()
    user.password = pwd_context.hash(getpass())
    db.session.commit()



@server_cli.command('list')
def list_servers():
    servers = db.session.query(YarraServer).all()
    for s in servers:
        print(s)

@server_cli.command('modes')
@click.argument('name')
def list_modes(name):
    modes = db.session.query(ModeModel).join(YarraServer).filter(YarraServer.name == name)
    for m in modes:
        print(m)

def init_db():
    db.create_all()
    admin_role = Role(name="admin")
    db.session.add(admin_role)
    submit_role = Role(name="submitter")
    db.session.add(submit_role)
    initial_admin = User(username="admin", email="admin@localhost", password=pwd_context.hash("admin"),roles=[admin_role,submit_role])
    db.session.add(initial_admin)
    
    # servers = [YarraServer(name='***REMOVED***',username='yarra',path='***REMOVED***', roles=[submit_role]), 
    #             YarraServer(name='***REMOVED***',username='yarra',path='***REMOVED***',roles=[admin_role])]

    # for s in servers:
    #     s.password = '***REMOVED***'
    #     s.update_modes()
    #     db.session.add(s)

    db.session.commit()

@server_cli.command("update")
def update_servers():
    for s in db.session.query(YarraServer).all():
        s.update_modes()
    db.session.commit()
   
@db_cli.command("init")
def init():
    init_db()
    print("OK")

@db_cli.command("reset")
def reset():
    if input("Really reset the entire database? (Y/N) ") != "Y":
        return
    db.drop_all(bind=None)
    init_db()
    print("OK")

def init_app(app):
    app.cli.add_command(user_cli)
    app.cli.add_command(server_cli)
    app.cli.add_command(db_cli)
