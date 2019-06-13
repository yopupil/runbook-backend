# encoding: utf-8
"""
Flask-RESTplus API registration module
======================================
"""

from flask import Blueprint

from app.extensions import api


def init_app(app, socketio, **kwargs):
    # pylint: disable=unused-argument
    api_v1_blueprint = Blueprint('api_bp', __name__, url_prefix='/api/v1')
    api.api_v1.init_app(api_v1_blueprint)

    # Add authentication via decorator
    # Note: There is no register_decorator method for Api
    # this means that we have to declare when we instantiate API
    # So as a workaround, we pass the decorator in app.extensions.api
    # This is bad ! But we don't have a workaround
    # api.api_v1.decorators.append(authenticate_api)

    # Enable/disable swagger config (This is dirty, but it's the only way)
    #api.api_v1._doc = app.config.get('ENABLE_SWAGGER_API', True)  # pylint: disable=protected-access
    # Register the REST API blueprint with Flask app
    app.register_blueprint(api_v1_blueprint)
