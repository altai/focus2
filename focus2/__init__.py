# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Focus2
# Copyright (C) 2012 Grid Dynamics Consulting Services, Inc
# All Rights Reserved
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.


import os.path
import pkgutil

import flask
import werkzeug
import werkzeug.utils
import MySQLdb
import json

from _version import __version__

DEBUG = False
CSRF_ENABLED = False
API_ENDPOINT = ''
SECRET_KEY = '1ecdf1e7-306f-4b82-8d2e-bee89bffd6c9'
APP_TEMP_DIR = '/var/lib/focus2/'


def application_factory(config=(), api_object=None,
                        api_object_path='focus2.api:client'):
    """Application factory.
    Accepts:
    - list of objects or string file paths to python modules to configure from,
    - optional custom Altai API client and path to import default client.
    """

    # load api client object
    if api_object is None:
        api_object = werkzeug.utils.import_string(api_object_path)

    # define custom application class
    class AppTemplate(flask.Flask):
        class request_globals_class(object):
            api = api_object

        jinja_options = werkzeug.ImmutableDict(
            extensions=['jinja2.ext.autoescape', 'jinja2.ext.with_'],
            autoescape=True)

        def make_response(self, rv):
            """Extend Flask behavior. We can return a dict from blueprint
            endpoint and will have corresponding template rendered with
            the dict as context.
            """
            if type(rv) is dict:
                template_name = os.path.join(
                    *flask.request.endpoint.split('.')) + '.html'
                result = flask.render_template(template_name, **rv)
            elif isinstance(rv, (list, tuple)) and len(rv) == 2:
                result = flask.render_template(rv[0], **rv[1])
            else:
                result = rv
            response = super(AppTemplate, self).make_response(result)
            return response
    app = AppTemplate(__name__)
    # configure
    app.config.from_object(__name__)
    for x in config:
        if isinstance(x, basestring):
            try:
                app.config.from_pyfile(x)
            except IOError:
                try:
                    app.config.from_envvar(x)
                except RuntimeError:
                    pass
        else:
            app.config.from_object(x)

    def connect(app):
        return MySQLdb.connect(host=app.config['DB_HOST'],
                               db=app.config['DB_NAME'],
                               user=app.config['DB_USER'],
                               passwd=app.config['DB_PASSWD'])

    @app.before_request
    def connect_db():
        flask.g.db = connect(flask.current_app)

    @app.after_request
    def close_connection(response):
        flask.g.db.commit()
        flask.g.db.close()
        return response

    db = connect(app)
    c = db.cursor()
    c.execute('show tables')
    need_commit = False
    tables = c.fetchall()
    if ('sessions',) not in tables:
        c.execute('CREATE TABLE sessions ('
            'id int not null primary key auto_increment, '
            'body text, mdate timestamp)')
        need_commit = True
    if ('dashboard_objects',) not in tables:
        c.execute('CREATE TABLE dashboard_objects ('
            'id varchar(40) not null primary key, body text)')
        need_commit = True
    if need_commit:
        db.commit()
    db.close()

    class MySessionInterface(flask.sessions.SessionInterface):
        class session_class(dict, flask.sessions.SessionMixin):
            pass

        def get_session_id(self, app, request):
            self._session_cookie_name = app.session_cookie_name
            return request.cookies.get(app.session_cookie_name)

        def set_session_id(self, session_id):
            flask.request.cookies.set(self._session_cookie_name, session_id)

        def open_session(self, app, request):
            self.session_id = self.get_session_id(app, request)
            if self.session_id is not None:
                c = flask.g.db.cursor()
                c.execute('SELECT body from sessions WHERE id = %s',
                          (self.session_id,))
                result = c.fetchone()
                if result is not None:
                    return self.session_class(json.loads(result[0]))
            s = self.session_class()
            s.new = True
            return s

        def save_session(self, app, session, response):
            if not session.modified:
                return
            c = flask.g.db.cursor()
            if self.session_id is not None:
                c.execute('SELECT 1 FROM sessions WHERE id = %s',
                          (self.session_id))
                result = c.fetchone()
                if result is None:
                    c.execute(
                        'INSERT (id, body) INTO sessions VALUES (%s, %s)',
                        (self.session_id, json.dumps(session)))
                    c.execute('SELECT last_insert_id()')
                    self.set_session_id(c.fetchone()[0])
            else:
                c.execute('UPDATE sessions SET body = %s WHERE id = %s',
                          (json.dumps(session)), self.session_id)

    app.session_interface = flask.sessions.SecureCookieSessionInterface()
    # register blueprints
    path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'blueprints')
    for _, name, _ in pkgutil.iter_modules([path]):
        app.register_blueprint(werkzeug.utils.import_string(
            'focus2.blueprints.%s.BP' % name))

    def url_for_other_page(page):
        args = flask.request.view_args.copy()
        args['page'] = page
        return flask.url_for(flask.request.endpoint, **args)
    app.jinja_env.globals['url_for_other_page'] = url_for_other_page

    @app.errorhandler(RuntimeError)
    def runtime_error(error):
        return flask.render_template('runtime_error.html', message=str(error))

    return app
