# encoding: utf-8
import re
from flask import request
from urllib.parse import urlparse, parse_qs
from flask_restplus_patched import Resource
from flask_socketio import SocketIO
from slugify import slugify
from app.extensions.api import Namespace

from app.modules.cells.utils import get_path_configs, hydrate_path_configs, hydrate_query_configs, get_query_configs

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


api = Namespace('cells', description='REST API for cell code')

socketio = SocketIO(message_queue='redis://redis:6379')


@api.route('/')
class CellOutputResource(Resource):
    def post(self):
        data = request.json
        socketio.emit('code_result', {
            'id': data['cellId'],
            'output': ''.join(data['lines']),
            'error': '',
            'streamType': data['streamType']
        }, room=data['channel'], namespace='/cells')


@api.route('/internal-endpoints/parse')
class CellEndpointArguments(Resource):

    def post(self):
        """Given endpoint url parse and return parameters"""

        try:
            body = request.json

            # Get endpoint config
            request_uri = body['requestUri']
            config = body['config']

            # Use path template to extract path arguments
            path_template = config['path']
            query_template = config['query']
            endpoint_name = config['name']

            # Get query arguments, path arguments etc from URL and replace
            result = urlparse(request_uri)
            request_path = result.path.replace('/endpoints/{}'.format(endpoint_name), '')

            # Hydrate values using request_path
            path_configs = hydrate_path_configs(path_template, get_path_configs(path_template), request_path)

            parsed_query = parse_qs(result.query)

            # Use the query configuration values to
            query_configs = hydrate_query_configs(get_query_configs(query_template), parsed_query)

            return {
                'path': {
                    p['arg']: p['value'] for p in path_configs
                },
                'query': {
                    q['arg']: q['value'] for q in query_configs
                }
            }
        except ValueError as e:
            return {
                'message': str(e)
            }, 400
