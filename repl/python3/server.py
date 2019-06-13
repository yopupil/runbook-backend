# encoding: utf-8
"""
Spawns a listener that is capable of executing python3 code.

The listener can execute code in several modes

a) REPL mode: using an instance of `code.InteractiveConsole`
b) File mode: execute code using `__main__` blocks and return output
c) Server mode: Spawn an endpoint that blocks and waits for response. The stdout will
be redirected to cell log output.

"""
import os
import re
import sys
import code
import time
import asyncio
import contextlib
import json
import requests

import logging
import tornado.ioloop
import tornado.web
import tornado.escape

from io import StringIO
from subprocess import Popen, PIPE
from asyncio.subprocess import PIPE
from flask_socketio import SocketIO
from urllib.parse import urlparse


__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


socketio = SocketIO(message_queue='redis://redis:6379')

SERVER_URI = os.environ['SERVER_URI']


def secure_file_path(file_path, root_dir):
    """Return a secure version of file path"""
    return os.path.abspath(os.path.join(root_dir, os.path.relpath(file_path.replace('~', ''), root_dir))).lstrip(os.sep)


# https://stackoverflow.com/questions/17190221/subprocess-popen-cloning-stdout-and-stderr-both-to-terminal-and-variables/25960956#25960956
async def read_stream_and_display(stream, display, stream_type, logging_interval=1):
    """Read from stream line by line until EOF, capture lines and call display method."""
    # Emit logs every x seconds
    start = time.time()
    lines = []
    while True:
        line = await stream.readline()
        if logging_interval == 0:
            if not line:
                break
            else:
                display([line.decode('utf-8')], stream_type)
                continue
        if not line:
            if len(lines):
                display(lines, stream_type)
            break
        time_elapsed = time.time() - start
        if time_elapsed > logging_interval:
            # Stream to socket using variable
            display(lines, stream_type)
            lines = []
            start = time.time()
        else:
            lines.append(line.decode('utf-8'))
    return True


async def read_and_display(payload, filename, *cmd):
    """Capture cmd's stdout, stderr while displaying them as they arrive
    (line by line).

    """
    # start process
    process = await asyncio.create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)

    def post_line_to_server(lines, stream_type):
        socketio.emit('code_result', {
            'id': payload['cellId'],
            'output': ''.join(lines).replace(filename, 'sh') if stream_type == 'stdout' else '',
            'error': ''.join(lines).replace(filename, 'sh') if stream_type == 'stderr' else '',
        }, room=payload['channel'], namespace='/cells')
    # read child's stdout/stderr concurrently (capture and display)
    try:
        await asyncio.gather(
            read_stream_and_display(process.stdout, post_line_to_server, 'stdout', 0),
            read_stream_and_display(process.stderr, post_line_to_server, 'stderr', 0))
    except Exception as e:
        process.kill()
        post_line_to_server([str(e)], 'stderr')
    finally:
        # wait for the process to exit
        rc = await process.wait()
    return rc


def capture_logs(payload, filename, *cmd):
    # run the event loop
    if os.name == 'nt':
        loop = asyncio.ProactorEventLoop() # for subprocess' pipes on Windows
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    if loop.is_running():
        # Tornado runs a default event loop
        # This is python 3.5.1 !!
        asyncio.run_coroutine_threadsafe(read_and_display(payload, filename, *cmd), loop)
    else:
        loop.run_until_complete(read_and_display(payload, filename, *cmd))


class REPLExecutionHandler(tornado.web.RequestHandler):
    """A request handler for executing repl code"""
    def initialize(self, console):
        self.console = console

    def create_temporary_shell_file(self, cell_id, code):
        filename = '/tmp/.file_{}.sh'.format(cell_id)
        with open(filename, 'w') as f:
            f.write(code)
        os.system('chmod +x ./{}'.format(filename))
        return filename

    def execute_repl(self, code, cell_id, channel):
        """Execute the code provided in cell with specified id"""
        # Execute code and on receiving input/output pipe them to server using callback_url
        out = StringIO()
        err = StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.console.runcode(code)
        except SyntaxError:
            self.console.showsyntaxerror()
        except:
            self.console.showtraceback()
        socketio.emit('code_result', {
            'id': cell_id,
            'output': out.getvalue(),
            'error': err.getvalue(),
        }, room=channel, namespace='/cells')

    def execute_shell(self, payload, code):
        filename = self.create_temporary_shell_file(payload['cellId'], code)
        # args = shlex.split()
        capture_logs(payload, filename, *['bash', filename])

    def execute_code(self, language, cell_id, channel, code):
        if language == 'shell':
            self.execute_shell({
                'channel': channel,
                'cellId': cell_id
            }, code)
            self.write('Ok')
        else:
            self.execute_repl(code, cell_id, channel)
            self.write('Ok')

    def get(self):
        code = self.get_query_argument('code')
        language = self.get_query_argument('language')
        channel = self.get_query_argument('channel')
        cell_id = self.get_query_argument('cellId')
        return self.execute_code(
            language,
            cell_id,
            channel,
            code
        )

    def post(self):
        language = self.get_query_argument('language')
        data = tornado.escape.json_decode(self.request.body)
        code = data['code']
        channel = data['channel']
        cell_id = data['cellId']
        return self.execute_code(
            language,
            cell_id,
            channel,
            code
        )


class FileExecutionHandler(tornado.web.RequestHandler):
    """A request handler for executing python files"""
    def initialize(self, file_path_root):
        self.file_path_root = file_path_root

    def execute_file(self, file_path):
        """Execute the code provided by the file path"""
        p = Popen([sys.executable, file_path], env={
            # Module discovery
            'PYTHONPATH': self.file_path_root
        }, stdout=PIPE, stderr=PIPE, cwd=self.file_path_root)
        stdout, stderr = p.communicate()
        return stderr.decode('utf-8'), stdout.decode('utf-8')

    def get(self):
        file_path = self.get_query_argument('path')
        err, out = self.execute_file(secure_file_path(file_path, self.file_path_root))
        self.write(json.dumps({
            'error': err,
            'output': out
        }))

    def post(self):
        file_data = tornado.escape.json_decode(self.request.body)
        file_path = secure_file_path(file_data['filePath'], self.file_path_root)
        file_content = file_data['content']
        full_path = os.path.normpath(os.path.join(self.file_path_root, file_path))
        base_dir = os.path.dirname(full_path)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        return self.write(file_path)


class PingHandler(tornado.web.RequestHandler):
    """A request handler for health status checks"""
    def get(self):
        return self.write('pong')


class EndpointsHandler(tornado.web.RequestHandler):
    """Handle endpoint related requests"""

    def initialize(self, file_path_root):
        self.file_path_root = file_path_root

    def post(self):
        # An endpoint is like a dynamic route. We execute the endpoint by storing the config in a certain location.
        # Once the request is received, we will use the config to parse the request and execute the code within
        body = tornado.escape.json_decode(self.request.body)

        # The file we are wrapping in an endpoint
        file_path = secure_file_path(body['filePath'], self.file_path_root)

        config = body['config']

        config['filePath'] = file_path

        full_path = os.path.normpath(os.path.join(self.file_path_root, 'endpoints', '{}.config'.format(config['name'])))
        base_dir = os.path.dirname(full_path)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        # The endpoint configuration, which we will write to a file (or load from store later on)
        with open(full_path, 'w') as f:
            f.write(json.dumps(body['config']))
        return self.write('Ok')


class EndpointsExecutionHandler(tornado.web.RequestHandler):

    def initialize(self, file_path_root):
        self.file_path_root = file_path_root

    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps({
            'error': {
                'code': status_code,
                'message': self._reason
            }
        }))

    def _execute_endpoint(self, file_path):
        """Execute the code provided by the file path"""
        p = Popen([sys.executable, file_path], env={
            # Module discovery
            'PYTHONPATH': self.file_path_root
        }, stdout=PIPE, stderr=PIPE, cwd=self.file_path_root)
        stdout, stderr = p.communicate()
        return stderr.decode('utf-8'), stdout.decode('utf-8')

    def _get_config(self, endpoint_name):
        full_path = os.path.normpath(os.path.join(self.file_path_root, 'endpoints', '{}.config'.format(endpoint_name)))

        if not os.path.exists(full_path):
            raise tornado.web.HTTPError(404, reason='Missing endpoint configuration for {}. Please check if endpoint is defined.'.format(endpoint_name))
        with open(full_path, 'r') as f:
            return json.loads(f.read())

    def _write_endpoint_file(self, config):
        file_path = config['filePath']

        full_path = os.path.normpath(os.path.join(self.file_path_root, file_path))

        if not os.path.exists(full_path):
            raise tornado.web.HTTPError(404, reason='Missing endpoint configuration for {}. Please check if endpoint is defined.'.format(config['name']))

        with open(full_path, 'r') as f:
            content = f.read()

            # Use the server to parse the request arguments
            response = requests.post(SERVER_URI + '/api/v1/cells/internal-endpoints/parse', json={
                'config': config,
                'requestUri': self.request.uri
            })
            
            if response.status_code == 400:
                raise tornado.web.HTTPError(reason=response.json()['message'], status_code=400)
            elif response.status_code == 200:
                response_body = response.json()

                query_args = response_body['query']
                path_args = response_body['path']

                variable_sets = ['{} = "{}"'.format(k, v) if isinstance(v, str) else '{} = {}'.format(k, v) for k, v in path_args.items()]

                # Map them out in file as well
                variable_sets += ['{} = "{}"'.format(k, v) if isinstance(v, str) else '{} = {}'.format(k, v) for k, v in query_args.items()]

                file_postfix_content = '\n'.join(variable_sets)

                content += '\n' + file_postfix_content

                content += '\n\nprint({})'.format(config['signature'])

                # Write to endpoint specific file
                endpoint_file = full_path.replace('.py', '') + '--endpoint.py'
                with open(endpoint_file, 'w') as wf:
                    wf.write(content + '\n')

                return endpoint_file
            else:
                raise tornado.web.HTTPError(reason='Error while attempting to parse endpoint {}'.format(
                    re.sub(r'\r\n', '', response.text)))

    def get(self, endpoint_name):
        # Run the specified endpoint using signature
        config = self._get_config(endpoint_name)
        # Create endpoint_file and execute endpoint file

        endpoint_file = self._write_endpoint_file(config)

        err, output = self._execute_endpoint(endpoint_file)

        if err and len(err):
            self.set_status(500)
            return self.write(err)
        else:
            self.set_status(200)
            return self.write(output)

    def post(self, endpoint_name):
        config = self._get_config(endpoint_name)
        endpoint_file = self._write_endpoint_file(config)

        err, output = self._execute_endpoint(endpoint_file)

        if err and len(err):
            self.set_status(500)
            return self.write(err)
        else:
            self.set_status(200)
            return self.write(output)


class Python3REPLServer:
    """The Python3 REPl server"""
    def __init__(self, file_path_root='/tmp/code-files'):
        # Setup the console
        self.console = code.InteractiveConsole()

        # File path root will help with script execution
        self.file_path_root = file_path_root

        # Create file path root
        if not os.path.exists(file_path_root):
            os.makedirs(file_path_root)

        # Each endpoint will run in a separate Thread. Otherwise the event loop will block the new server endpoints.
        # We ideally expect a single kernel to have few endpoints. Creating lots of endpoints is not performant.
        # The server will proxy requests/responses to/from the endpoint processes.
        self._endpoint_threads = {}

    def execute_endpoint(self, cell_id, file_path):
        """Spawn a separate process that acts as a server endpoint."""
        # The server should maintain a state about the forked process.
        # If the code at file_path changes, the server must restart the process
        # so this is stateful
        raise NotImplementedError()

    def start(self):
        """Start a new REPL server"""
        app = tornado.web.Application([
            (r"/ping", PingHandler),
            (r"/repl", REPLExecutionHandler, dict(console=self.console)),
            (r"/file", FileExecutionHandler, dict(file_path_root=self.file_path_root)),
            (r"/endpoints", EndpointsHandler, dict(file_path_root=self.file_path_root)),
            (r"/endpoints/(?P<endpoint_name>[\w\-\d]+).*", EndpointsExecutionHandler, dict(file_path_root=self.file_path_root))
        ])
        app.listen(1111)
        logging.info('Started Python 3 Kernel...')
        tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    Python3REPLServer().start()
