"""
This module only contains common routes used for app and static asset management.
For resource specific routes and REST APIs refer to app.modules.xxyy.{views,templates} instead
"""
from flask import jsonify, send_from_directory, abort, render_template

from app.extensions.auth import authenticate_route, authenticate_api

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'

SITE_ADMINISTRATION_NAMESPACE = 'manage'


def init_app(app):
    """Register common routes and endpoints for serving static files"""

    app.url_map.strict_slashes = False

    @app.route('/')
    @app.route('/<path:path_name>')
    def catch_all_others(path_name=None):
        return abort(404)
