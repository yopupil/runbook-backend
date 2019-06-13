# encoding: utf-8
# pylint: disable=invalid-name,wrong-import-position,wrong-import-order
"""
Extensions setup
================
Extensions provide access to common resources of the application.
Please, put new extension instantiations and initializations here.
"""

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'

from .logging import Logging
logging = Logging()

from .flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from sqlalchemy_utils import force_auto_coercion, force_instant_defaults
force_auto_coercion()
force_instant_defaults()

from flask_marshmallow import Marshmallow
marshmallow = Marshmallow()

from flask_migrate import Migrate
migrate = Migrate()

from . import auth
from . import api
from . import csrf
from . import session

def init_app(app):
    """
    Application extensions initialization.
    """
    for extension in (
            logging,
            db,
            session,
            marshmallow,
            api
        ):
        extension.init_app(app)

        # Register flask migrate
        migrate.init_app(app, db)
