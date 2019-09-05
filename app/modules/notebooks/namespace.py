# encoding: utf-8
"""

Notebooks namespace handlers

namespace = '/notebooks'

A handler for managing notebooks in the system
"""
import logging
import requests
from flask import request
from flask_socketio import Namespace, emit, disconnect


from app.extensions.api import SocketIONamespace

logger = logging.getLogger(__name__)

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


class NotebookSocketEvents:
    CREATE_NOTEBOOK_REQUEST = 'SocketEvent::CREATE_NOTEBOOK_REQUEST'
    CREATE_NOTEBOOK_RESPONSE = 'SocketEvent::CREATE_NOTEBOOK_RESPONSE'


class NotebooksNamespace(SocketIONamespace):
    def __init__(self):
        super().__init__('/notebooks')
        self.handler_dict = {
            NotebookSocketEvents.CREATE_NOTEBOOK_REQUEST: self.create_notebook
        }

    def create_notebook(self, payload):
        """Create a new notebook in the system"""
        # Store in durable storage.
        notebook_service.create_notebook(payload)
        # FE will write notebook to disk periodically upon save/change
        self.emit(
            NotebookSocketEvents.CREATE_NOTEBOOK_RESPONSE,
            data={
                'id': 'chooral',
                'focus': 'mene'
            },
            namespace=self.namespace, room=request.sid
        )

    # Convert the notebook definitions into kubectl definitions ? What we are running is effectively
    # a container, we don't need storage.
    # But what about the cell metadata ? Where will that be persisted ?

    # Instead of using docker SDK directly then, orechestrator will wrap over and
    # provide some naive orchestration using docker. For production we will use kubectl

    # Some cell definitions require file mounts. Is this possible with kube ?
