# encoding: utf-8
"""
API extension
=============
"""
import os
from flask import current_app, render_template
from flask_restplus_patched import Api

from .namespace import Namespace
from .http_exceptions import abort, api_abort
from .socketio_namespace import SocketIONamespace

from ..auth.decorators import authenticate_api

api_v1 = Api(# pylint: disable=invalid-name
    version='1.0',
    title='Expense Processing App REST API',
    decorators=[]
)


def render_custom_swaggerui():
    return render_template('swagger-ui.html')


def init_app(app, **kwargs):
    # pylint: disable=unused-argument
    """
    API extension initialization point.
    """
    # Remove the `default` namespace
    api_v1.namespaces.clear()

    app.route('/swaggerui/swagger-ui.html')(render_custom_swaggerui)
    app.logger.info('Registering api extension')
