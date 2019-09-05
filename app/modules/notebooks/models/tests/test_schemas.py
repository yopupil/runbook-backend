# coding: utf8
import pytest
from datetime import datetime, timezone

from ..notebook import Notebook
from ..schemas import NotebookSchema

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


@pytest.mark.unit
@pytest.mark.notebooks
def test_schema_load_required_fields():
    s = NotebookSchema()
    l = s.load({
        'id': 'foo',
        'name': 'foobar'
    })
    assert isinstance(l, Notebook)
    assert l.id == 'foo'
    assert l.name == 'foobar'
    assert l.description == ''


@pytest.mark.unit
@pytest.mark.notebooks
def test_schema_load_optional_date_fields():
    s = NotebookSchema()
    l = s.load({
        'id': 'foo',
        'name': 'foobar',
        'created_at': '2019-01-02T12:22:33.000Z'
    })
    assert isinstance(l, Notebook)
    assert isinstance(l.created_at, datetime)
    assert l.created_at.year == 2019
    assert l.created_at.month == 1
    assert l.created_at.day == 2
    assert l.created_at.hour == 12
    assert l.created_at.minute == 22


@pytest.mark.unit
@pytest.mark.notebooks
def test_schema_dump():
    s = NotebookSchema()
    n = Notebook(
        id='foo',
        name='foobar',
        description='food',
        created_at=datetime(2019, 1, 2, 12, 22, 33, tzinfo=timezone.utc),
        updated_at=datetime(2019, 1, 2, 12, 22, 35, tzinfo=timezone.utc)
    )
    l = s.dump(n)
    assert isinstance(l, dict)
    assert l['id'] == 'foo'
    assert l['name'] == n.name
    assert l['description'] == n.description
    assert l['created_at'] == '2019-01-02 12:22:33.000Z'
    assert l['updated_at'] == '2019-01-02 12:22:35.000Z'




