# coding: utf8
import os
import json

from app.utils import get_logger

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
    def get_config(directory):
        """Get runtime config for a given runtime directory.

        Parameters
        ----------
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
                    return json.loads(config)
                except (ValueError, TypeError):
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

        path = os.path.join(app_config[key])
        logger.info('Loading runtime configs')

        # Scan the directory using os.scandir
        with os.scandir(path) as it:

            # Process each entry
            for entry in it:

                # Ignore hidden folders
                if not entry.name.startswith('.') and entry.is_dir():

                    # Get config
                    config = self.get_config(os.path.join(path, entry.name))

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
