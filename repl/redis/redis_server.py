# encoding: utf-8
import socket
import os

import tornado.ioloop
import tornado.web
import tornado.escape

from flask_socketio import SocketIO

# From from https://github.com/supercoderz/redis_kernel

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'

socketio = SocketIO(message_queue='redis://redis:6379')


class RedisResponseParser(object):
    """Redis response parser"""
    def __init__(self, response, commands=False):
        self.response = response
        self.result = []
        self.is_array = False
        self.is_error = False
        if not commands:
            self.parse_response()
        else:
            self.parse_commands()

    def parse_commands(self):
        # get each section of the command response
        sections = self.response.split('*6\r\n')
        for section in sections:
            parts = section.split('\r\n')
            # only the second one is the command name
            # no need to parse for now
            if parts[1] is not None and parts[1].__len__() > 0:
                self.result.append(parts[1])

    def parse_response(self):
        # get each line of the response
        parts = self.response.split('\r\n')

        if parts[0].startswith('*'):
            self.is_array = True

        for part in parts:
            if part != '':
                value = self.parse_part(part)
                if value is not None:
                    self.result.append(value)

    def parse_part(self, part):
        if part[0] == '*':
            # array count
            return None
        elif part[0] in ['-', '+', ':']:
            if part[0] == '-':
                self.is_error = True
                #error or string or integer
                return part[1:]
            elif part[0] == '+':
                return part[1:]
            elif part[0] == ':':
                return int(part[1:])
        elif part[0] == '$':
            if part[1:] == '-1':
                # handle nil
                return 'nil'
            else:
                # ignore the byte count
                return None
        else:
            # values returned after the type specifier
            return part

    def _repr_html_(self):
        res = self.get_result()
        if self.is_error:
            out = "<p style='color:red'>" + res + '</p>'
        else:
            out = res
        return out

    def _repr_text_(self):
        return self.get_result()

    def get_result(self):
        if self.result.__len__() > 1:
            out = []
            for x in self.result:
                if isinstance(x, int):
                    out.append(str(x))
                else:
                    out.append(x)
            return out
        elif self.result.__len__() > 0:
            if type(self.result[0] == int):
                return str(self.result[0])
            else:
                return self.result[0]
        else:
            self.is_error = True
            return 'Error executing command. There was no result.'


class REPLExecutionHandler(tornado.web.RequestHandler):
    """A request handler for executing repl code"""
    def initialize(self, host='localhost', port='6379'):
        self.host = host
        self.port = port
        self.connected = False
        self.redis_socket = None
        self.connect()

    def connect(self):
        """Start a connection to specified redis instance."""
        if self.redis_socket is None:
            host = self.host
            port = self.port
            sock = None
            # loop through all connection options
            for res in socket.getaddrinfo(host, port):
                try:
                    family, stype, protocol, name, address = res
                    sock = socket.socket(family, stype, protocol)
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    sock.connect(address)
                    # just half a second timeout
                    sock.settimeout(0.25)
                    self.redis_socket = sock
                    self.connected = True
                    # and return on the first successful one
                    return
                except Exception as e:
                    import logging
                    logging.exception('error')
                    # Truncate connection on error
                    self.connected = False
                    if sock is not None:
                        sock.close()

    def recv_all(self):
        total_data = []
        while True:
            try:
                data = self.redis_socket.recv(1024)
            except socket.timeout:
                # sink any timeout here
                break
            if data is None:
                break
            total_data.append(data)
        return ''.encode('utf-8').join(total_data)

    def execute_code(self, cell_id, channel, code):
        """Execute the lines of code in Redis."""
        if not (code[-2:] == '\r\n'):
            code = code.strip() + '\r\n'
        self.redis_socket.send(code.encode('utf-8'))
        response = self.recv_all()
        data = RedisResponseParser(response.decode('utf-8'))
        result = data.get_result()

        socketio.emit('code_result', {
            'id': cell_id,
            'output': '' if data.is_error else result,
            'error': '' if not data.is_error else result
        }, room=channel, namespace='/cells')

        return self.write('Ok')

    def get(self):
        code = self.get_query_argument('code')
        channel = self.get_query_argument('channel')
        cell_id = self.get_query_argument('cellId')
        return self.execute_code(
            cell_id,
            channel,
            code
        )

    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        code = data['code']
        channel = data['channel']
        cell_id = data['cellId']
        return self.execute_code(
            cell_id,
            channel,
            code
        )


class PingHandler(tornado.web.RequestHandler):
    """A request handler for health status checks"""
    def get(self):
        return self.write('pong')


class RedisREPLServer:
    """Start a HTTP server that will invoke commands by passing to Redis.

    Adapted from https://github.com/supercoderz/redis_kernel

    This kernel uses a socket connection to talk to redis.
    """
    def __init__(self, host='redis', port='6379'):
        self.connected = False
        self.host = host
        self.port = port
        self.redis_socket = None

    def start(self, host=None, port=None):
        """Start a new REPL server"""
        app = tornado.web.Application([
            (r"/ping", PingHandler),
            (r"/repl", REPLExecutionHandler, dict(
                host=host,
                port=port
            ))
        ])
        app.listen(1111)
        tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    server = RedisREPLServer()
    REDIS_HOST = os.environ['REDIS_HOST']
    REDIS_PORT = os.environ['REDIS_PORT']
    server.start(host=REDIS_HOST, port=REDIS_PORT)
