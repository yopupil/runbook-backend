# encoding: utf-8

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


def init_app(app, socketio):

    from .namespace import CodeFilesNamespace

    socketio.on_namespace(CodeFilesNamespace())
