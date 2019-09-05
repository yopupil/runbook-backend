# coding: utf8
from functools import wraps
from flask_socketio import Namespace

__author__ = 'Tharun Mathew Paul (tharun@bigpiventures.com)'


class SocketIONamespace(Namespace):
    """A subclass of Flask SocketIO namespace"""

    def __init__(self, namespace):
        super().__init__(namespace)
        self.handler_dict = {}

    def trigger_event(self, event, *args):
        """Trigger events received from socket"""
        handler = self.handler_dict.get(event, None)
        if not handler:
            return
        else:
            return self.socketio._handle_event(handler, event, self.namespace, *args)
