# -*- coding: utf-8 -*-
"""
Functional test suite for the root controller.

This is an example of how functional tests can be written for controllers.

As opposed to a unit-test, which test a small unit of functionality,
functional tests exercise the whole application and its WSGI stack.

Please read http://pythonpaste.org/webtest/ for more information.

"""
from nose.tools import ok_
from nose.tools import eq_
from rubrica.tests import TestController
from rubrica.model import Contatto
from rubrica.model import DBSession

class TestRootController(TestController):
    """Tests for the method in the root controller."""

    def test_index(self):
        """Testa il response di index"""
        res = self.app.get('/index',)
        ok_(res.location.startswith('http://localhost/login'))

        "Testa il response da loggati"
        environ = {'REMOTE_USER': 'manager'}
        resp = self.app.get('/index', extra_environ=environ, status=200)
        contatto1 = DBSession.query(Contatto).first()
        msg1 = "<td>{}</td><td>{}</td>".format(contatto1.name, contatto1.phone)
        resp.mustcontain(msg1)

    def test_add_form(self):
        """Testa l'add dei contatti"""
        environ = {'REMOTE_USER': 'manager'}
        self.app.get('/add', extra_environ=environ, status=200)

    def test_save(self):
        """Testa il save dei contatti"""
        environ = {'REMOTE_USER': 'manager'}
        resp = self.app.post('/save', extra_environ=environ, status=200)
        form = resp.form
        form['nome'] = 'manager'
        form['telefono'] = '123456'
        form.submit(extra_environ=environ)

        contatti = DBSession.query(Contatto).all()
        last = contatti[-1]
        eq_(last.name, 'manager')
        eq_(last.phone, '123456')

        "Testa input errato"
        environ = {'REMOTE_USER': 'manager'}
        resp = self.app.post('/save', extra_environ=environ, status=200)
        form = resp.form
        form['nome'] = '123'
        form['telefono'] = 'abc'
        form.submit(extra_environ=environ, status=200)
        contatto = DBSession.query(Contatto).all()
        last = contatto[-1]
        ok_(last.name != '123')

    def test_esponi(self):
        """Testa se il response di esponi è corretto"""
        environ = {'REMOTE_USER': 'manager'}
        resp = self.app.get('/esponi', extra_environ=environ, status=200)
        contatto1 = DBSession.query(Contatto).first()
        string = '"phone": "{}", "id": {}, "name": "{}"'.format(contatto1.phone, contatto1.id, contatto1.name)
        resp.mustcontain(string)

    def test_download(self):
        """test download"""
        environ = {'REMOTE_USER': 'manager'}
        resp = self.app.get('/download', extra_environ=environ, status=200)
        header = resp.headers
        ok_('Content-Type', 'applications/json' in header)
        ok_('Content-Disposition', 'attachment;filename=rubrica.json' in header)

    def test_delete(self):
        """Testa delete contatto"""
        environ = {'REMOTE_USER': 'manager'}
        resp = self.app.post('/save', extra_environ=environ, status=200)
        form = resp.form
        form['nome'] = 'manager'
        form['telefono'] = '123456'
        form.submit(extra_environ=environ)
        contatti = DBSession.query(Contatto).all()
        last = contatti[-1]
        self.app.get('/delete?item_id={}'.format(last.id), extra_environ=environ, status=302)
        contatti = DBSession.query(Contatto).all()
        contatto2 = contatti[-1]
        ok_(last != contatto2)

        resp = self.app.post('/delete?item_id=999', extra_environ=environ, status=302)
        ok_('Set-Cookie:', 'Il contatto non esiste' in resp.headers)

    def test_environ(self):
        """Displaying the wsgi environ works"""
        response = self.app.get('/environ.html')
        ok_('The keys in the environment are:' in response)

    def test_data(self):
        """The data display demo works with HTML"""
        response = self.app.get('/data.html?a=1&b=2')
        response.mustcontain("<td>a", "<td>1",
                             "<td>b", "<td>2")

    def test_data_json(self):
        """The data display demo works with JSON"""
        resp = self.app.get('/data.json?a=1&b=2')
        ok_(
            dict(page='data', params={'a': '1', 'b': '2'}) == resp.json,
            resp.json
        )
    """
    def test_secc_with_manager(self):
        "The manager can access the secure controller"
        # Note how authentication is forged:
        environ = {'REMOTE_USER': 'manager'}
        resp = self.app.get('/secc', extra_environ=environ, status=200)
        ok_('Secure Controller here' in resp.text, resp.text)
    """
    def test_secc_with_editor(self):
        """The editor cannot access the secure controller"""
        environ = {'REMOTE_USER': 'editor'}
        self.app.get('/secc', extra_environ=environ, status=403)
        # It's enough to know that authorization was denied with a 403 status

    def test_secc_with_anonymous(self):
        """Anonymous users must not access the secure controller"""
        self.app.get('/secc', status=401)
        #It's enough to know that authorization was denied with a 401 status
