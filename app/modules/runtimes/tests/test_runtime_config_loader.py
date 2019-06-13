# coding: utf8
import pytest
import os
import json
import shutil
from contextlib import contextmanager

from ..config_loader import RuntimeConfigLoader

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'

@contextmanager
def create_temporary_runtimes(*configs):
    try:
        for name, config in configs:
            os.makedirs('/tmp/.runtimes/{}'.format(name))
            with open('/tmp/.runtimes/{}/.unklearn.config'.format(name), 'w') as f:
                f.write(json.dumps(config) if isinstance(config, dict) else config)
        yield
    finally:
        shutil.rmtree('/tmp/.runtimes')


@pytest.mark.unit
@pytest.mark.runtimes
def test_runtime_config_loader_load_no_install_folder():

    with pytest.raises(RuntimeError):
        RuntimeConfigLoader().load({})
        RuntimeConfigLoader().load({
            'RUNTIME_INSTALLATION_FOLDER': ''
        })


@pytest.mark.unit
@pytest.mark.runtimes
def test_runtime_config_loader_load():
    # Make a directory and install dummy runtime
    with create_temporary_runtimes(('test-runtime', {'name': 'test-runtime'})):

        loader = RuntimeConfigLoader()
        loader.load({
            'RUNTIME_INSTALLATION_FOLDER': '/tmp/.runtimes'
        })

        assert len(loader.runtime_configs) == 1
        assert loader.runtime_configs[0]['name'] == 'test-runtime'


@pytest.mark.unit
@pytest.mark.runtimes
def test_runtime_config_loader_incorrect_config():
    with create_temporary_runtimes(('test-runtime', {'name': 'test-runtime'}), ('incorrect-runtime', 'wrong config')):
        loader = RuntimeConfigLoader()
        loader.load({
            'RUNTIME_INSTALLATION_FOLDER': '/tmp/.runtimes'
        })

        assert len(loader.runtime_configs) == 1
        assert loader.runtime_configs[0]['name'] == 'test-runtime'
