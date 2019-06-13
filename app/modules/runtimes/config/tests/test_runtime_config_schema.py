# coding: utf8
import pytest
from marshmallow import ValidationError

from ..schemas import ClientRuntimeConfigSchema, SourceRuntimeConfigSchema

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


@pytest.mark.unit
@pytest.mark.runtimes
@pytest.mark.parametrize('schema', [ClientRuntimeConfigSchema(), SourceRuntimeConfigSchema()])
def test_client_runtime_schema_load(schema):

    with pytest.raises(ValidationError):
        schema.load({})
        schema.load({
            'name': 'test-runtime'
        })
        schema.load({
            'name': 'test-runtime',
            'image': 'python'
        })
        schema.load({
            'name': 'test-runtime',
            'image': 'python',
            'tag': 'latest'
        })
        schema.load({
            'name': 'test-runtime',
            'image': 'python',
            'tag': 'latest',
            'modes': [1]
        })
        schema.load({
            'name': 'test-runtime',
            'image': 'python',
            'tag': 'latest',
            'modes': ['wrong']
        })

    val = {
        'name': 'test-runtime',
        'image': 'python',
        'tag': 'latest',
        'modes': ['interactive']
    }
    assert schema.load(val) == {
        'name': 'test-runtime',
        'image': 'python',
        'tag': 'latest',
        'modes': ['interactive'],
        'languages': []
    }


@pytest.mark.unit
@pytest.mark.runtimes
def test_source_runtime_schema():
    schema = SourceRuntimeConfigSchema()
    val = {
        'name': 'test-runtime',
        'image': 'python',
        'tag': 'latest',
        'modes': ['interactive'],
        'dockerfile_template': '''
        FROM {{image}}:{{version}}
        '''
    }
    assert schema.load(val) == {
        'name': 'test-runtime',
        'image': 'python',
        'tag': 'latest',
        'modes': ['interactive'],
        'languages': [],
        'dockerfile_template': '''
        FROM {{image}}:{{version}}
        '''
    }
