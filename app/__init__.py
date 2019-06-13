"""
Expense Processing application
"""
import logging
import os
import sys

from flask import Flask
from flask_socketio import SocketIO


CONFIG_NAME_MAPPER = {
    'development': 'config.DevelopmentConfig',
    'testing': 'config.TestingConfig',
    'production': 'config.ProductionConfig',
    'local': 'local_config.LocalConfig',
    'ci': 'config.CITestingConfig'
}


def create_app(flask_config_name=None, **kwargs):
    """
    Entry point to the Flask RESTful Server application.
    """
    # This is a workaround for Alpine Linux (musl libc) quirk:
    # https://github.com/docker-library/python/issues/211
    import threading
    threading.stack_size(2*1024*1024)

    app = Flask(__name__, static_url_path='/app/static', **kwargs)

    # Retrive environment to use
    env_flask_config_name = os.getenv('FLASK_ENVIRONMENT_TYPE')

    if not env_flask_config_name and flask_config_name is None:
        flask_config_name = 'local'
    elif flask_config_name is None:
        flask_config_name = env_flask_config_name
    else:
        if env_flask_config_name:
            assert env_flask_config_name == flask_config_name, (
                "FLASK_ENVIRONMENT_TYPE environment variable (\"%s\") and flask_config_name argument "
                "(\"%s\") are both set and are not the same." % (
                    env_flask_config_name,
                    flask_config_name
                )
            )
    app.logger.info('Using configuration for environment {}'.format(env_flask_config_name))

    try:
        app.config.from_object(CONFIG_NAME_MAPPER[flask_config_name])
    except ImportError:
        if flask_config_name == 'local':
            app.logger.error(
                "You have to have `local_config.py` or `local_config/__init__.py` in order to use "
                "the default 'local' Flask Config. Alternatively, you may set `FLASK_ENVIRONMENT_TYPE` "
                "environment variable to one of the following options: development, production, "
                "testing."
            )
            sys.exit(1)
        raise

    socketio = SocketIO(app, message_queue='redis://redis:6379')

    from . import extensions
    extensions.init_app(app)

    from . import modules
    modules.init_app(app, socketio)

    # Register common routes
    from . import routes
    routes.init_app(app)

    return app, socketio
