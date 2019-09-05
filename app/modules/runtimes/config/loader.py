# coding: utf8
import os
import re
import json
from marshmallow.exceptions import ValidationError

from app.utils import get_logger

from .schemas import SourceRuntimeConfigSchema

logger = get_logger(__name__)

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


class RuntimeConfigLoader:
    """
    Load the available runtimes found in RUNTIME_INSTALLATION_FOLDER
    """

    def __init__(self):
        self.runtime_configs = []

    def init_app(self, app):
        """Initialize the loader."""
        self.load(app.config)

    @staticmethod
    def get_subset(source, target):
        """Return only items in source that are present in target.

        If there are no matches, full object is returned.

        Example
        >>> get_subset(['a', 'b'], ['b'])
        >>> ['b']

        >>> get_subset(['a', 'b'], ['c'])
        >>> ['a', 'b']
        """
        final = list()
        for item in target:
            if item not in source:
                continue
            else:
                final.append(item)

        if not len(final):
            return source
        else:
            return final

    @staticmethod
    def get_config(runtime, directory):
        """Get runtime config for a given runtime directory.

        Parameters
        ----------
        runtime: str
            The name of the runtime

        directory: str
            The runtime directory

        Returns
        -------
            The runtime configuration as dictionary or None if it cannot be found
        """
        config_path = os.path.join(directory, '.unklearn.config')
        if not os.path.exists(config_path):
            return None
        else:
            with open(config_path, 'r') as f:
                config = f.read()
                try:
                    return SourceRuntimeConfigSchema().load(json.loads(config))
                except (ValueError, TypeError):
                    return None
                except ValidationError as e:
                    raise Exception('Validation error while reading runtime config for {}:{}'.format(runtime, e))

    def get_matching_runtime(self, runtime_def):
        """Find a matching defined runtime config and return it.

        The returned config will have overridden values

        Parameters
        ---------
        runtime_def: dict
            The client side runtime definition
        """
        for config in self.runtime_configs:
            if config['image'] == runtime_def['image']:
                # Use tag to match
                pattern = re.compile(config['tag'])
                # First matching pattern is selected
                if pattern.match(runtime_def['tag']):
                    return {
                        'name': runtime_def['name'],
                        'image': config['image'],
                        'tag': runtime_def['tag'],
                        'modes': RuntimeConfigLoader.get_subset(config['modes'], runtime_def.get('modes', [])),
                        'languages': RuntimeConfigLoader.get_subset(config['languages'], runtime_def.get('languages', []))
                    }
        return None

    def load(self, app_config):
        """Load runtime configurations

        Parameters
        ----------
        app_config: dict
            The flask app config

        Raises
        ------
        RuntimeError: if configuration key value is not set
        """

        key = 'RUNTIME_INSTALLATION_FOLDER'

        if key not in app_config or (key in app_config and not app_config[key]):
            raise RuntimeError('Application config must define {} value'.format(key))

        # Get path to file
        path = app_config[key]

        logger.info('Loading runtime configs')

        # Scan the directory using os.scandir
        with os.scandir(path) as it:

            # Process each entry
            for entry in it:

                # Ignore hidden folders
                if not entry.name.startswith('.') and entry.is_dir():

                    # Get config
                    config = self.get_config(entry.name, os.path.join(path, entry.name))

                    # Warn if no config
                    if config:
                        logger.info('Adding runtime config for {}'.format(entry.name))
                        self.runtime_configs.append(config)
                    else:
                        logger.warning('Could not find config for {} in runtime directory. '
                                       'Please make sure that it is a valid runtime'.format(entry.name))

        logger.info('Finished processing runtime configs. Available runtimes are {}'.format(
            ','.join([c['name'] for c in self.runtime_configs])
        ))


runtime_config_loader = RuntimeConfigLoader()
