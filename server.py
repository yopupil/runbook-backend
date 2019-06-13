import os
import logging

import eventlet
eventlet.monkey_patch()

from app import create_app
from flask import request

# We define it here so that flask migrate can run commands
app, socketio = create_app(flask_config_name=os.environ['FLASK_ENVIRONMENT_TYPE'])

if __name__ == '__main__':
    PUBLISH_PORT = os.getenv('INTERNAL_API_PUBLISH_PORT', 8763)
    DEBUG = os.getenv('INTERNAL_API_DEBUG', False)
    logging.basicConfig(level=logging.INFO)
    logging.info('Publish port ' + str(PUBLISH_PORT))

    if app.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.log(logging.INFO, 'Setting debug mode to true')

    socketio.run(app, host="0.0.0.0", port=int(PUBLISH_PORT), debug=app.debug)
