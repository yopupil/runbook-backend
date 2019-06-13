# encoding: utf-8
"""

Code files namespace handlers

namespace = '/code-files'

These handlers are responsible for saving and mounting files on running containers. Saving a file on a container
allows us to execute code and import modules and functions from other code files.


The files are always mounted at a specific root path in the container. Attempts to use relative path for file mounting
will fail.
"""
import logging
import requests
from flask import request
from flask_socketio import Namespace, emit


from app.modules.cells.namespace import EmittedCellEvents

logger = logging.getLogger(__name__)

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


class EmittedCodeFileEvents:
    CODE_FILE_NAME = 'code_file_name'


class CodeFilesNamespace(Namespace):
    def __init__(self):
        super().__init__('/code-files')

    def on_code_file_create(self, payload):
        """Create a new kernel with the provided data"""
        # Create a server that will accept requests from user land to execute code cells in an interactive
        # sandbox. The server can also spawn `endpoints` which are essentially servers like Express.js, Flask,
        # Django etc etc. What should this server be written in ? And how should it execute code ? e.g interactive
        # python shell means the kernel should spawn and startup `code.InteractiveConsole`. This will lead to code
        # being executed in a sandbox. Use pre-created images that support a variety of language specific tweaks.

        # Once the container is created, we need to execute commands that are specific to the language and framework.
        # These commands will setup the REPL code.

        # Create a new kernel using docker SDK
        sid = request.sid
        kernel = payload['kernel']
        cell_id = payload['cellId']
        file_path = payload['filePath']
        content = payload['content']

        logger.info('Mounting file {file_path} in kernel {kernel}'.format(
            file_path=file_path,
            kernel=kernel
        ))

        # Route the request to the container so that it can create the file

        try:
            resp = requests.post('http://{}:1111/file'.format(kernel), json={
                'content': content,
                'filePath': file_path,
                'cellId': cell_id,
                'channel': sid
            })
            if resp.status_code == 200:
                self.emit(EmittedCodeFileEvents.CODE_FILE_NAME, {
                    'id': payload['cellId'],
                    'filePath': resp.text.strip()
                }, namespace=self.namespace, room=sid)
        except requests.exceptions.ConnectionError:
            emit(EmittedCellEvents.CODE_RESULT, {
               'id': cell_id,
               'error': 'Cannot find kernel {}'.format(kernel),
               'output': ''
            }, namespace=self.namespace, room=sid)


