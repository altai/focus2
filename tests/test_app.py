import tempfile
import unittest

import flask
import flask.ctx

from focus2 import application_factory


class Configuration(unittest.TestCase):
    def test_configure(self):
        """Test the factory configures the app according to passed paths and
        objects in correct order
        """
        app = application_factory()
        self.assertNotEqual(app, None)


class Autoescape(unittest.TestCase):
    def test_app_env(self):
        app = application_factory()
        self.assertTrue(app.jinja_env.autoescape)
        self.assertIn('jinja2.ext.AutoEscapeExtension',
                      app.jinja_env.extensions)


class G(unittest.TestCase):
    def test_correct_class(self):
        app = application_factory()
        with app.test_request_context('/'):
            self.assertNotIsInstance(flask.g, flask.ctx._RequestGlobals)
