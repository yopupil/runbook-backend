"""
Redis backed session for app
"""
from flask_session import Session

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


def init_app(app):
    app.secret_key = app.config['SECRET_KEY']
    session = Session()
    session.init_app(app)
    app.logger.info('Registering Session extension')
