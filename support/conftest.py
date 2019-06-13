import pytest
import flask_bcrypt
import os
from flask import Flask, url_for, template_rendered

from app import create_app
from app.extensions import db, migrate

from support.json_test_client import JSONTestClient


def check_password_hash(h, p):
    return h == p


@pytest.fixture(scope='session')
def app():
    # Replace bcrypt methods to enable faster tests
    _o1 = flask_bcrypt.generate_password_hash
    _o2 = flask_bcrypt.check_password_hash
    flask_bcrypt.generate_password_hash = lambda x: x
    flask_bcrypt.check_password_hash = lambda h, p: h == p

    a = create_app(flask_config_name=os.getenv('TEST_ENV', 'testing'))
    a.test_client_class = JSONTestClient

    yield a

    # Restore
    flask_bcrypt.generate_password_hash = _o1
    flask_bcrypt.check_password_hash = _o2


@pytest.fixture(scope='session')
def client(app):
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = app.test_client(use_cookies=True)

    # Establish an application context before running the tests.
    ctx = app.test_request_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


@pytest.fixture(scope='function')
def database(client):
    # Create tables
    db.create_all()
    # Create the database and the database table
    yield db
    # Remove session
    db.session.remove()
    # Drop all tables
    db.drop_all()


# To test if a view is rendered
@pytest.fixture(scope='function')
def captured_templates(app):
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)
