# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, lurl
from tg import request, redirect, tmpl_context, response
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.exceptions import HTTPFound
from tg import predicates
from rubrica import model
from rubrica.controllers.secure import SecureController
from rubrica.model import DBSession
from tgext.admin.tgadminconfig import BootstrapTGAdminConfig as TGAdminConfig
from tgext.admin.controller import AdminController

from rubrica.lib.base import BaseController
from rubrica.controllers.error import ErrorController

from rubrica.model.contatto import Contatto
from tg.decorators import paginate
from tw2.forms import DataGrid
from markupsafe import Markup

tabella = DataGrid(fields=[
    ('Name: ', 'name'),
    ('Phone: ', 'phone'),
    ('', lambda obj: Markup('<a href="%s" onclick="return confirm(\'Sei sicuro?\');">Delete</a>' % url('/delete', params=dict(item_id=obj.id))))
])

__all__ = ['RootController']


class RootController(BaseController):
    """
    The root controller for the rubrica application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    secc = SecureController()
    admin = AdminController(model, DBSession, config_type=TGAdminConfig)

    error = ErrorController()

    def _before(self, *args, **kw):
        tmpl_context.project_name = "rubrica"

    @paginate("data", items_per_page=10)
    @expose('rubrica.templates.index')
    def index(self):
        """handle index page"""
        if not request.identity:
            redirect('/login')
        data = DBSession.query(Contatto).filter_by(owner=request.identity['user'].user_id)
        return dict(page='index', grid=tabella, data=data)

    @expose('json')
    def esponi(self):
        """Espone la rubrica in formato JSON"""
        data = DBSession.query(Contatto).filter_by(owner=request.identity['user'].user_id).all()
        return dict(data=data)

    @expose('json')
    def download(self):
        """Download della rubrica"""
        data = DBSession.query(Contatto).filter_by(owner=request.identity['user'].user_id).all()
        response.content_type = 'applications/json'
        response.headerlist.append(('Content-Disposition', 'attachment;filename=rubrica.json'))
        return dict(data=data)

    @expose(template='rubrica.templates.add')
    def add(self):
        """Aggiunge contatto"""
        return dict(page='add')

    @expose()
    def save(self, name, phone):
        """Salva il contatto aggiunto con /add"""
        if name and phone and name.isalpha() and phone.isdigit():
            contatto = Contatto(name=name, phone=phone)
            request.identity['user'].contacts.append(contatto)
            DBSession.add(contatto)
            redirect('/index')
        else:
            raise ValueError('Errore, il form deve essere compilato correttamente: name=[A-z], phone=[0-9]')

    @expose()
    def delete(self, item_id):
        """Elimina contatto"""
        contatto = DBSession.query(Contatto).get(item_id)
        DBSession.delete(contatto)
        redirect('/index')

    @expose('rubrica.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    @expose('rubrica.templates.environ')
    def environ(self):
        """This method showcases TG's access to the wsgi environment."""
        return dict(page='environ', environment=request.environ)

    @expose('json')
    @expose('rubrica.templates.data')
    def data(self, **kw):
        """
        This method showcases how you can use the same controller
        for a data page and a display page.
        """
        return dict(page='data', params=kw)

    @expose('rubrica.templates.index')
    @require(predicates.has_permission('manage', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('rubrica.templates.index')
    @require(predicates.is_user('editor', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')

    @expose('rubrica.templates.login')
    def login(self, came_from=lurl('/'), failure=None, login=''):
        """Start the user login."""
        if failure is not None:
            if failure == 'user-not-found':
                flash(_('User not found'), 'error')
            elif failure == 'invalid-password':
                flash(_('Invalid Password'), 'error')

        login_counter = request.environ.get('repoze.who.logins', 0)
        if failure is None and login_counter > 0:
            flash(_('Wrong credentials'), 'warning')

        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from, login=login)

    @expose()
    def post_login(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ.get('repoze.who.logins', 0) + 1
            redirect('/login',
                     params=dict(came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)

        # Do not use tg.redirect with tg.url as it will add the mountpoint
        # of the application twice.
        return HTTPFound(location=came_from)

    @expose()
    def post_logout(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        return HTTPFound(location=came_from)
