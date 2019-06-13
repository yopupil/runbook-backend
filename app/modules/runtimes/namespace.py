# encoding: utf-8
"""

Runtime namespace handlers

namespace = '/runtimes'

These handlers are responsible for creating the necessary runtime to run the notebook. A runtime is simply
a sandbox execution environment provided inside an isolated container tied to the user's unique session. It is very
similar to Jupyter Kernel, but we provide a range of extra functionalities on top.


Our runtimes provide both REPL like code execution, and execution of files mounted into the container. REPL like
behavior allows them to easily test newly created functions etc, while file based code execution emulates realistic
projects, and can create server endpoints which can block REPL code execution.

"""
import logging
import requests
from flask import request, current_app
from flask_socketio import Namespace, emit, SocketIO

from app.modules.runtimes.config_loader import runtime_config_loader


logger = logging.getLogger(__name__)

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


class EmittedRuntimeEvents:
    """An enum class representing emitted events for runtime namespace"""
    CREATED = 'runtime_created'
    LOG = 'runtime_log'
    STATUS = 'status'


class RuntimesNamespace(Namespace):
    def __init__(self):
        super().__init__('/runtimes')
        # Runtime namespace

    def on_create_runtime(self, runtime_def):
        """Create a new runtime with the provided data"""

        # Try to find a matching runtime.
        # Runtimes are loaded by reading .unklearn.config files
        runtime = runtime_config_loader.match_runtime(runtime_def)

        # Use the runtime's Dockerfile.template to generate a dockerfile
        runtime.docker_file_template

        # Use the Dockerfile.template to create the runtime

        # Wait for the runtime health to return 200.
        # Ports => Proxied ports with specified protocol
        # Proxy: proxy ports from container so that front-end can talk to it via a proxy.
        # localhost:8763/portals/flask_runtime_id/web => goes to [flask app]

        # Processing dependencies

        # Once the container is created, we need to execute commands that are specific to the language and framework.
        # These commands will setup the REPL code.

        # Create a new kernel using docker SDK
        sid = request.sid
        logger.info('Creating {runtime} for socket {socket}'.format(runtime=runtime_def['name'], socket=sid))

        # Find registered kernel creators, and run them when we need to start the container
        image = runtime_def['image']

        # Find from registry and create the container

        runtime_handler = None

        container = runtime_handler.create(runtime_def)

        # Create the reference name for the container.
        unique_name = kernel_def['notebook_id'] + '_' + kernel_def['name']

        # Emit the corresponding event so fe can update
        emit(EmittedKernelEvents.KERNEL_CREATED, {
            # We use the namespaced name as id and not container.id so that front-end can disambiguate ids
            'id': unique_name,
            'name': kernel_def['name'],
            'version': kernel_def['version'],
            # This field will be used to identify the container using network
            'value': unique_name,
            'supportedLanguages': kernel_def.get('supportedLanguages', None),
            'image': kernel_def['image'],
            'notebookId': kernel_def['notebook_id']
        }, namespace=self.namespace, room=sid)

        logger.info('Waiting for kernel to be ready')
        # Post message to background worker so that it can wait for kernel logs and ready status
        self.socketio.start_background_task(self._wait_for_kernel, current_app._get_current_object(), sid, container, unique_name)

    """
    Private methods
    """

    def _create_kernel(self, kernel_def):
        """Create a new kernel based on python image and version"""
        # Check if an image already exists with given `image` and `version`
        image = kernel_def['image']
        cls = BaseKernelCreator.get_creator_by_image(image)
        if not cls:
            raise RuntimeError('Cannot find a creator for specified image {}'.format(image))
        return cls.create(kernel_def)

    def _wait_for_kernel(self, app, sid, container, unique_name, timeout=120):
        with app.app_context():
            offset = 0
            time = 0
            sio = SocketIO(message_queue='redis://redis:6379')
            while True:
                if time > timeout:
                    sio.emit(EmittedKernelEvents.KERNEL_LOG, {
                        'id': unique_name,
                        'logs': ['ERROR: Kernel timed out...']
                    })
                    return sio.emit(EmittedKernelEvents.KERNEL_STATUS, {
                        'id': unique_name,
                        'status': 'error'
                    })
                kernel_name = container.name
                # Make request. If the kernel responds, then we emit STATUS event,
                # else we poll again
                try:
                    logs = [l for l in container.logs().decode('utf-8').split('\n')[offset:] if l]
                    offset += len(logs)
                    emit(EmittedKernelEvents.KERNEL_LOG, {
                        'id': unique_name,
                        'logs': logs
                    }, namespace=self.namespace, room=sid)
                    logger.debug(logs)
                    resp = requests.get('http://{}:1111/ping'.format(kernel_name))
                    if resp.status_code == 200:
                        logger.info('Kernel {} is ready'.format(kernel_name))
                        emit(EmittedKernelEvents.KERNEL_STATUS, {
                            'id': unique_name,
                            'status': 'ready'
                        }, namespace=self.namespace, room=sid)
                        return True
                    else:
                        raise requests.exceptions.ConnectionError()
                    # Check every second
                except requests.exceptions.ConnectionError:
                    sio.sleep(1)
                    time += 1
