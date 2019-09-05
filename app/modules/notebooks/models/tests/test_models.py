# coding: utf8
import pytest
from datetime import datetime

from ..notebook import Notebook

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


@pytest.mark.unit
@pytest.mark.notebooks
def test_notebook_model():
    dt = datetime.now()
    n = Notebook(
        id='foo',
        name='name',
        description='desc',
        created_at=dt,
        updated_at=dt
    )

    assert n.id == 'foo'
    assert n.name == 'name'
    assert n.description == 'desc'
    assert n.created_at == dt
    assert n.updated_at == dt


@pytest.mark.unit
@pytest.mark.notebooks
def test_notebook_model_merge():
    dt = datetime.now()
    second_dt = datetime.now().replace(year=3000)
    n = Notebook(
        id='foo',
        name='name',
        description='desc',
        created_at=dt,
        updated_at=dt
    )
    n.merge({
        'id': 'bookey',
        'name': 'falsey',
        'created_at': second_dt,
        'updated_at': second_dt
    })

    assert n.name == 'falsey'
    assert n.id == 'foo', 'id must not change after merge'
    assert n.created_at == dt, 'created_at date must not change after merge'
    assert n.updated_at == second_dt
