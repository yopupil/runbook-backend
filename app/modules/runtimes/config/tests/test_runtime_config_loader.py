# coding: utf8
import pytest
import os
import json
import shutil
from contextlib import contextmanager

from ..loader import RuntimeConfigLoader
from ..schemas import SourceRuntimeConfigSchema

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'

sample_runtime_config = {'name': 'test-runtime', 'image': 'python', 'tag': 'latest'}

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
    with create_temporary_runtimes(('test-runtime', sample_runtime_config)):

        loader = RuntimeConfigLoader()
        loader.load({
            'RUNTIME_INSTALLATION_FOLDER': '/tmp/.runtimes'
        })

        assert len(loader.runtime_configs) == 1
        assert loader.runtime_configs[0]['name'] == 'test-runtime'

@pytest.mark.unit
@pytest.mark.runtimes
def test_runtime_config_loader_invalid_config():
    with create_temporary_runtimes(('test-runtime', {})):
        loader = RuntimeConfigLoader()
        with pytest.raises(Exception):
            loader.load({
                'RUNTIME_INSTALLATION_FOLDER': '/tmp/.runtimes'
            })

@pytest.mark.unit
@pytest.mark.runtimes
def test_runtime_config_loader_wrong_config_file_type():
    with create_temporary_runtimes(('test-runtime', sample_runtime_config), ('incorrect-runtime', 'wrong config')):
        loader = RuntimeConfigLoader()
        loader.load({
            'RUNTIME_INSTALLATION_FOLDER': '/tmp/.runtimes'
        })

        assert len(loader.runtime_configs) == 1
        assert loader.runtime_configs[0]['name'] == 'test-runtime'


@pytest.mark.unit
@pytest.mark.runtimes
def test_runtime_config_loader_ignore_files():
    with create_temporary_runtimes(('test-runtime', sample_runtime_config)):

        # Hidden file
        with open('/tmp/.runtimes/.ignore-runtime', 'w') as f:
            f.write('test')

        # Regular file
        with open('/tmp/.runtimes/ignore-runtime', 'w') as f:
            f.write('test')

        loader = RuntimeConfigLoader()
        loader.load({
            'RUNTIME_INSTALLATION_FOLDER': '/tmp/.runtimes'
        })

        assert len(loader.runtime_configs) == 1
        assert loader.runtime_configs[0]['name'] == 'test-runtime'


@pytest.mark.unit
@pytest.mark.runtimes
def test_loader_subset():

    assert RuntimeConfigLoader.get_subset(['a', 'b'], ['c']) == ['a', 'b']
    assert RuntimeConfigLoader.get_subset(['a', 'b'], ['a']) == ['a']
    assert RuntimeConfigLoader.get_subset(['a', 'b'], ['a', 'b']) == ['a', 'b']


@pytest.mark.unit
@pytest.mark.runtimes
def test_runtime_config_loader_matching_runtime():

    loader = RuntimeConfigLoader()
    loader.runtime_configs = [{
        'name': 'test-runtime',
        'image': 'python',
        'tag': 'latest',
        'languages': ['shell', 'python'],
        'modes': ['files']
    }, {
        'name': 'test-runtime',
        'image': 'mysql',
        'tag': '(3.*)|(latest)',
        'languages': ['shell', 'sql'],
        'modes': ['interactive']
    }]

    assert loader.get_matching_runtime({
        'name': 'tt',
        'image': 'python',
        'tag': 'latest',
        'languages': ['shell']
    }) == {
        'name': 'tt',
        'image': 'python',
        'tag': 'latest',
        'languages': ['shell'],
        'modes': ['files']
    }

    assert loader.get_matching_runtime({
        'name': 'tt',
        'image': 'python',
        'tag': 'latest',
        'languages': ['wrong'],
        'modes': ['incorrect']
    }) == {
       'name': 'tt',
       'image': 'python',
       'tag': 'latest',
       'languages': ['shell', 'python'],
       'modes': ['files']
   }
