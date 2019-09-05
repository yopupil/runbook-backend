# coding: utf8
import os
from docker import from_env, types as docker_types, errors as docker_errors

from app.utils import get_container_id, get_host_path, get_container_network

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


class RuntimeHandler:

    @staticmethod
    def start_container_if_exited(client, container_name):
        """Start a docker container if it is in exited state.

        Parameters
        ----------
        client: DockerClient
            The docker client

        container_name: str
            The name of the container
        """
        matching_containers = client.containers.list(all=True, filters={
            'name': container_name
        })

        # Docker ps returns partial matches. So a string like `new_py3` will match `new_py351`
        matching_containers = [c for c in matching_containers if c.name == container_name]

        if matching_containers and len(matching_containers):
            container = matching_containers[0]
            if container.status == 'exited':
                container.start()
            return container
        return None

    @staticmethod
    def create(runtime_def):
        """Create a new runtime based on given runtime configuration

        Parameters
        ----------
        runtime_def: dict
            The runtime definition

        Returns
        -------
        container: docker.Container
            The created docker container
        """
        # Check if an image already exists with given `image` and `tag`
        client = from_env()
        image = runtime_def['image']
        tag = runtime_def['tag']

        container_name = runtime_def['name']

        container = RuntimeHandler.start_container_if_exited(client, container_name)

        if container:
            return container

        try:
            client.images.get('{}:{}'.format(image, tag))
        except docker_errors.ImageNotFound:
            # Pull the image from dockerhub
            client.images.pull('{}:{}'.format(image, tag))

        # Spawn a container with given image that uses the same network as current container.
        # What if we are running `bare-metal` ? In this case, the ports need to be exposed,
        # and the details must be stored in the notebook state.
        return client.containers.run('{}:{}'.format(image, tag),
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
