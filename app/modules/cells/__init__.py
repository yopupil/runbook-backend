# encoding: utf-8
from app.extensions.api import api_v1

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


def init_app(app, socketio):

    from .namespace import CellsNamespace
    from .resources import api

    socketio.on_namespace(CellsNamespace())

    api_v1.add_namespace(api, path='/cells')
