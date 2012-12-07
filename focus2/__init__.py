__version__ = '0.0.1'

import os.path
import pkgutil

import flask
import werkzeug


DEBUG = False
CSRF_ENABLED = False


class AppTemplate(flask.Flask):
    jinja_options = werkzeug.ImmutableDict(
        extensions=['jinja2.ext.autoescape'],
        autoescape=True
    )

    def make_response(self, rv):
        if type(rv) is dict:
            template_name = os.path.join(flask.request.endpoint.split('.'))
            result = flask.render_template(
                template_name + '.html', **rv)
        elif isinstance(rv, (list, tuple)) and len(rv) == 2:
            result = flask.render_template(rv[0], **rv[1])
        else:
            result = rv
        return super(FatFlask, self).make_response(result)
    
    

def application_factory(*args):
    app = AppTemplate(__name__)

    # configure
    app.config.from_object(__name__)
    for x in args:
        if isinstance(x, basestring):
            app.config.from_pyfile(x)
        else:
            app.config.from_object(x)
    path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'blueprints')
    for importer, name, _ in pkgutil.iter_modules([path]):
        full_name = 'focus2.blueprints.%s' % name
        module = importer.find_module(full_name).load_module(full_name)
        if 'BP' in dir(module):
            app.register_blueprint(module.BP)
    return app
