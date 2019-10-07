from flask.cli import AppGroup
from extensions import db
from models import User, Role, YarraServer, ModeModel
import click
from getpass import getpass

user_cli = AppGroup('user')
server_cli = AppGroup('server')
db_cli = AppGroup('db')

@user_cli.command('create')
@click.argument('name')
def create_user(name):
    roles = [db.session.query(Role).filter_by(name=r).scalar() for r in ['admin','submitter']]
    pw = getpass()
    new_user =  User(username=name, password=pwd_context.hash(pw),roles=roles)
    db.session.add(new_user)
    db.session.commit()
    print("Done")

@user_cli.command('list')
def list_users():
    users = db.session.query(User).all()
    for u in users:
        print(u, ", ".join([role.name for role in u.roles]))

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


def init_db():
    db.create_all()
    admin_role = Role(name="admin")
    db.session.add(admin_role)
    submit_role = Role(name="submitter")
    db.session.add(submit_role)
    test_user = User(username="roy", password=pwd_context.hash("roy"),roles=[admin_role,submit_role])
    db.session.add(test_user)
    tobias = User(username="tobias", password=pwd_context.hash("tobias"),roles=[admin_role,submit_role])
    db.session.add(tobias)


    servers = [YarraServer(name='AGR1',path='xdglpdcdap001.nyumc.org', roles=[submit_role]), 
                YarraServer(name='YarraAda',path='xdglpdcdap002.nyumc.org',roles=[admin_role])]

    for s in servers:
        s.update_modes()
        db.session.add(s)

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
    db.drop_all()
    init_db()
    print("OK")

def init_app(app):
    app.cli.add_command(user_cli)
    app.cli.add_command(server_cli)
    app.cli.add_command(db_cli)