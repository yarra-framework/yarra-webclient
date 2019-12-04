from flask import Blueprint, render_template, abort
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash,send_from_directory
from extensions import login_required, db
from models import User, Role, YarraServer, ModeModel
from flask.views import View
from forms import NewForm, LoginForm
from extensions import pwd_context

class ObjectView(View):
    def __init__(self, asset_model,view_func):
        self.Model = asset_model
        self.Form = self.Model.form
        self.view_func = view_func

    def on_updated(self, asset):
        pass

    def dispatch_request(self,identifier,method):
        assets = self.Model.query.all()

        if method == 'new':
            asset = self.Model()
        elif len(assets)==0:
            return redirect(url_for('admin.'+self.view_func,method='new'))
        elif not identifier:
            return redirect(url_for('admin.'+self.view_func,identifier=assets[0].get_id(), method=method))
        else:
            asset = self.Model.query.filter_by(**{self.Model.get_id_field():identifier}).first()

        if not asset:
            return redirect(url_for('admin.'+self.view_func,identifier=assets[0].get_id(), method=method))
        form = self.Form(obj=asset)

        if request.method == 'POST':
            if method == 'delete': #todo: csrf
                db.session.delete(asset)
                db.session.commit()
                flash("Deleted.","primary")
                return redirect(url_for('admin.'+self.view_func,method='edit'))

            if form.validate_on_submit():
                form.populate_obj(asset)
                self.on_updated(asset)
                if method == 'new':
                    db.session.add(asset)
                    db.session.commit()

                    flash("Created","primary")
                    return redirect(url_for('admin.'+self.view_func,method='edit'))

                db.session.commit()
                flash('Submitted.','primary')
                return redirect(request.referrer)

        view_name="Servers"
        if (self.view_func=="role_edit"):
            view_name="Roles"
        if (self.view_func=="user_edit"):
            view_name="Users"

        return render_template('asset-edit.html',admin_views=admin_views,asset=asset,assets=assets,form=form,new_form=NewForm(),view_func=self.view_func,view_name=view_name)

class UserView(ObjectView):
    def on_updated(self,asset):
        asset.password = pwd_context.hash(asset.password)
    
    def dispatch_request(self,identifier,method):
        if method == 'delete' and identifier in ('admin',):
            flash('This user cannot be removed.','warning')
            return redirect(request.referrer)
        return super(UserView, self).dispatch_request(identifier,method)

class ServerView(ObjectView):
    def on_updated(self,asset):
        try:
            asset.update_modes()
        except Exception as e:
            flash("Warning: "+str(e),'warning')

class RoleView(ObjectView):

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
def register_view( model, path, view_name, view_title, viewClass=ObjectView):
	admin_views.append(dict(view_name=view_name,name=model.__name__,title=view_title))
	view = viewClass.as_view(view_name, model,view_name)
	view = login_required('admin')(view)

	admin.add_url_rule('/admin/{}/'.format(path), view_func=view, defaults={'method':'edit','identifier': None})
	admin.add_url_rule('/admin/{}/<method>/'.format(path),view_func=view,defaults={'identifier': None}, methods=['GET','POST'])
	admin.add_url_rule('/admin/{}/<method>/<identifier>'.format(path),view_func=view,methods=['GET','POST'])

admin = Blueprint('admin', __name__,
                        template_folder='templates')


@admin.route('/admin/')
@login_required()
def admin_page():
    return redirect(url_for(".server_edit"))

register_view(YarraServer,'server','server_edit','<i class="fas fa-network-wired"></i> Servers',ServerView)
register_view(User,'user','user_edit','<i class="fas fa-users"></i> Users',UserView)
register_view(Role,'role','role_edit','<i class="fas fa-tags"></i> Roles',RoleView)
