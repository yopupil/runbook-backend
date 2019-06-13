# encoding: utf-8
import os
import subprocess
from docker import from_env, errors

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


# https://stackoverflow.com/questions/20010199/how-to-determine-if-a-process-runs-inside-lxc-docker
def is_a_docker_container():
    """ Determines if we're running in an lxc/docker container. """
    out = subprocess.check_output('cat /proc/1/cgroup', shell=True)
    out = out.decode('utf-8').lower()
    checks = [
        'docker' in out,
        '/lxc/' in out,
        out.split('\n')[0] not in ('systemd', 'init',),
        os.path.exists('/.dockerenv'),
        os.path.exists('/.dockerinit'),
        os.getenv('container', None) is not None
    ]
    return any(checks)


def get_container_id():
    """Determine if the current host is a container and if it is return the id of the container"""
    if not is_a_docker_container():
        return None
    client = from_env()

    out = subprocess.check_output('cat /proc/1/cgroup', shell=True)
    out = out.decode('utf-8').lower()

    # Split the output
    container_id = out.split('\n')[0].split('/')[-1]

    # Verify that container exists
    try:
        client.containers.get(container_id)
        return container_id
    except errors.NotFound:
        return None


def get_host_path(container_id, mounted_path):
    """Get path on host if the mounted path contains a mounted volume."""
    # TODO: Tharun we assume single directory mount, we do not test for subdirectory mounts
    if not is_a_docker_container():
        return mounted_path
    client = from_env()

    try:
        container = client.containers.get(container_id)

        for mount_point in container.attrs['Mounts']:
            if mount_point['Type'] == 'bind' and mount_point['Destination'] in mounted_path:
                mounted_path = mounted_path.replace(mount_point['Destination'], mount_point['Source'])
        return mounted_path
    except errors.NotFound:
        return mounted_path


def get_container_network(container_id):
    if not is_a_docker_container():
        return None
    client = from_env()

    try:
        container = client.containers.get(container_id)
        return container.attrs['HostConfig']['NetworkMode']
    except errors.NotFound:
        return None
    except KeyError:
        return None
