# encoding: utf-8

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


class BaseKernelCreator:

    registry = {}

    @staticmethod
    def register_kernel_creator(image):
        def wrapper(cls):
            BaseKernelCreator.registry[image] = cls
            return cls

        return wrapper

    @staticmethod
    def get_creator_by_image(image):
        return BaseKernelCreator.registry.get(image, None)

    @staticmethod
    def start_container_if_exited(client, container_name):
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
    def create(kernel_def):
        raise NotImplementedError()
