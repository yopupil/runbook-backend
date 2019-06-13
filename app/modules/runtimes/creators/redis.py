# encoding: utf-8
import os
from docker import from_env, types as docker_types, errors as docker_errors

from app.utils import get_container_id, get_host_path, get_container_network
from .base import BaseKernelCreator


__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


@BaseKernelCreator.register_kernel_creator('redis')
class RedisKernelCreator(BaseKernelCreator):

    @staticmethod
    def create(kernel_def):
        """Create a new kernel based on redis image and version"""
        # Check if an image already exists with given `image` and `version`
        client = from_env()
        image = kernel_def['image']
        version = kernel_def.get('version', 'latest')

        # Check if there is already a container scoped to sid and with given name
        # in that case, simply return that container

        # Names must be scoped to notebook as well to allow imports
        container_name = kernel_def['notebook_id'] + '_' + kernel_def['name']

        redis_container_name = container_name + '_' + 'dbi'

        main_container = RedisKernelCreator.start_container_if_exited(client, container_name)
        db_container = RedisKernelCreator.start_container_if_exited(client, redis_container_name)

        if not db_container:
            try:
                client.images.get('{}:{}'.format(image, version))
            except docker_errors.ImageNotFound:
                # Pull the image / We don't support custom Dockerfile currently
                client.images.pull('{}:{}'.format(image, version))

            basedir = os.path.abspath(__file__)
            final_path = os.path.normpath(os.path.join(basedir, '../../../../../repl/{}'.format(image)))

            # Check if this is running inside a docker container, if so obtain mounted volume if it exists.
            # If the files are copied or `ADD`ed into the container, it cannot be located by docker daemon,
            # and command will fail
            container_id = get_container_id()
            if container_id:
                # Get volume mounts
                final_path = get_host_path(container_id, final_path)

            # Run redis db instance
            client.containers.run(
                # Run the redis db instance with specified version
                '{}:{}'.format(kernel_def['image'], kernel_def.get('version', 'latest')),
                name=redis_container_name,
                network=get_container_network(container_id),
                detach=True

            )

        if main_container:
            return main_container
        else:
            return client.containers.run(
                'python:3.5',
                '/bin/sh /opt/current/start.sh',
                detach=True,
                mounts=[
                    docker_types.Mount('/opt/current', final_path, 'bind')
                ],
                environment={
                    'REDIS_HOST': redis_container_name,
                    'REDIS_PORT': '6379',
                    'SERVER_URI': 'http://internal-api:8763'
                },
                network=get_container_network(container_id),
                name=container_name
            )
