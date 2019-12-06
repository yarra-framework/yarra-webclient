from flask import Blueprint, render_template, abort
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash,send_from_directory
from extensions import login_required, db
from models import User, Role, YarraServer, ModeModel
from flask.views import View
from forms import NewForm, LoginForm
from extensions import pwd_context

class ObjectView(View):
    view_title = "Unknown"
    icon = ""
    name = "unknown"
    def __init__(self):
        self.Model = self.__class__.model
        self.Form = self.Model.form
        
    def on_updated(self, asset):
        pass

    def dispatch_request(self,identifier,method):
        assets = self.Model.query.all()

        view_name = '.'+self.__class__.name

        if method == 'new':
            asset = self.Model()
        elif len(assets)==0:
            return redirect(url_for(view_name,method='new'))
        elif not identifier:
            return redirect(url_for(view_name,identifier=assets[0].get_id(), method=method))
        else:
            asset = self.Model.query.filter_by(**{self.Model.get_id_field():identifier}).first()

        if not asset:
            return redirect(url_for(view_name,identifier=assets[0].get_id(), method=method))
        form = self.Form(obj=asset)

        if request.method == 'POST':
            if method == 'delete': #todo: csrf
                db.session.delete(asset)
                db.session.commit()
                flash("Deleted.","primary")
                return redirect(url_for(view_name,method='edit'))

            if form.validate_on_submit():
                form.populate_obj(asset)
                self.on_updated(asset)
                if method == 'new':
                    db.session.add(asset)
                    db.session.commit()
                    flash("Created","primary")
                    return redirect(url_for(view_name,method='edit'))

                db.session.commit()
                flash('Updated','primary')
                return redirect(request.referrer)

        return render_template('asset-edit.html',
            admin_views=admin_views,
            asset=asset,
            assets=assets,
            form=form,
            new_form=NewForm(),
            view_name=view_name,
            view_title=self.__class__.view_title)

class UserView(ObjectView):
    view_title = "Users"
    icon = "users"
    name = "user_edit"
    model = User
    def on_updated(self,asset):
        asset.password = pwd_context.hash(asset.password)
    
    def dispatch_request(self,identifier,method):
        if method == 'delete' and identifier in ('admin',):
            flash('This user cannot be removed.','warning')
            return redirect(request.referrer)
        return super(UserView, self).dispatch_request(identifier,method)

class ServerView(ObjectView):
    view_title = "Servers"
    icon = "network-wired"
    name = "server_edit"
    model = YarraServer
    def on_updated(self,asset):
        try: # Load the modes from the server.
            asset.update_modes()
        except Exception as e: # if it fails, the server URL may be wrong
            flash("Warning: "+str(e),'warning')

class RoleView(ObjectView):
    view_title = "Roles"
    icon = "tags"
    name = "role_edit"
    model = Role
    def dispatch_request(self,identifier,method):
        if method == 'delete' and identifier in ('admin', 'submitter'):
            flash('This role cannot be removed.','warning')
            return redirect(request.referrer)

        if method=='new':
            self.Form.name.kwargs['render_kw']['readonly'] = False
        else:
            self.Form.name.kwargs['render_kw']['readonly'] = True

        return super(RoleView, self).dispatch_request(identifier,method)

admin_views = []
def register_view( path, viewClass):

    view = viewClass.as_view(viewClass.name)

    admin_views.append(dict(view_name='admin.'+viewClass.name,
                            icon=viewClass.icon,
                            title=viewClass.view_title))

    view = login_required('admin')(view)

    admin.add_url_rule('{}/'.format(path), view_func=view, defaults={'method':'edit','identifier': None})
    admin.add_url_rule('{}/<method>/'.format(path),view_func=view,defaults={'identifier': None}, methods=['GET','POST'])
    admin.add_url_rule('{}/<method>/<identifier>'.format(path),view_func=view,methods=['GET','POST'])

admin = Blueprint('admin', __name__,
                        template_folder='templates')


@admin.route('/admin/')
@login_required()
def admin_page():
    return redirect(url_for(".server_edit"))

register_view('server',ServerView)
register_view('user', UserView)
register_view('role', RoleView)
