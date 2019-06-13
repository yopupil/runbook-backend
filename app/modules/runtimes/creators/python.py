# encoding: utf-8
import os
from docker import from_env, types as docker_types, errors as docker_errors

from app.utils import get_container_id, get_host_path, get_container_network
from .base import BaseKernelCreator


__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


@BaseKernelCreator.register_kernel_creator('python')
class PythonKernelCreator(BaseKernelCreator):

    @staticmethod
    def create(kernel_def):
        """Create a new kernel based on python image and version"""
        # Check if an image already exists with given `image` and `version`
        client = from_env()
        image = kernel_def['image']
        version = kernel_def.get('version', 'latest')

        # Check if there is already a container scoped to sid and with given name
        # in that case, simply return that container

        # Names must be scoped to notebook as well to allow imports
        container_name = kernel_def['notebook_id'] + '_' + kernel_def['name']

        container = PythonKernelCreator.start_container_if_exited(client, container_name)

        if container:
            return container
        first_part = version.split('.')[0]
        if str(version) == 'latest':
            folder_tag = '3'
        elif int(float(first_part)) == 3:
            folder_tag = '3'
        else:
            folder_tag = '2'
        tag = image + folder_tag
        try:
            client.images.get('{}:{}'.format(image, version))
        except docker_errors.ImageNotFound:
            # Pull the image / We don't support custom Dockerfile currently
            client.images.pull('{}:{}'.format(image, version))

        basedir = os.path.abspath(__file__)
        final_path = os.path.normpath(os.path.join(basedir, '../../../../../repl/{}'.format(tag)))

        # Check if this is running inside a docker container, if so obtain mounted volume if it exists.
        # If the files are copied or `ADD`ed into the container, it cannot be located by docker daemon,
        # and command will fail
        container_id = get_container_id()
        if container_id:
            # Get volume mounts
            final_path = get_host_path(container_id, final_path)

        # Spawn a container with given image that uses the same network as current container.
        # What if we are running `bare-metal` ? In this case, the ports need to be exposed,
        # and the details must be stored in the notebook state.
        return client.containers.run('{}:{}'.format(
            kernel_def['image'],
            kernel_def.get('version', 'latest')),
            '/bin/sh /opt/current/start.sh',
            detach=True,
            mounts=[
                docker_types.Mount('/opt/current', final_path, 'bind')
            ],
            environment={
                'SERVER_URI': 'http://internal-api:8763'
            },
            # TODO: Tharun create a new network to talk. When server is not running inside a docker
            # container we cannot use container network
            network=get_container_network(container_id),
            name=container_name
        )
