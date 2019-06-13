# encoding: utf-8
"""

Cell namespace handlers

namespace = '/cells'

Handle code execution, cell content save etc

"""
import requests
from flask import request
from flask_socketio import Namespace, emit

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


class EmittedCellEvents:
    """An enum class representing emitted events"""
    CODE_RESULT = 'code_result'


class CellsNamespace(Namespace):

    def __init__(self):
        super().__init__('/cells')

    def on_code_run(self, payload):
        """Run the code in the given cell using REPL mode"""
        cell_id = payload['cellId']
        kernel_id = payload['kernelId']
        code = payload['code']
        language = payload['language']
        cell_type = payload['cellType']
        # If cell type is a file send to file handler
        sid = request.sid
        try:
            if cell_type == 'file':
                file_path = payload['filePath']
                resp = requests.get('http://{}:1111/file?path={}'.format(kernel_id, file_path)).json()
                emit(EmittedCellEvents.CODE_RESULT, {
                    'id': cell_id,
                    'error': resp['error'],
                    'output': resp['output']
                })
            else:
                requests.post('http://{}:1111/repl?language={}'.format(kernel_id, language), json={
                    'code': code,
                    'cellId': cell_id,
                    'channel': sid
                })
        except requests.exceptions.ConnectionError:
            emit(EmittedCellEvents.CODE_RESULT, {
               'id': cell_id,
               'error': 'Cannot find kernel {}'.format(kernel_id),
               'output': ''
            }, namespace=self.namespace, room=sid)

    def on_endpoint_create(self, payload):
        """Create a new endpoint for the given kernel."""
        cell_id = payload['cellId']
        kernel_id = payload['kernelId']
        requests.post('http://{}:1111/endpoints'.format(kernel_id), json={
            'config': payload['config'],
            'filePath': payload['filePath']
        })
