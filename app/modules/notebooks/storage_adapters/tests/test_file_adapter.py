# coding: utf8
import pytest
from pyfakefs.fake_filesystem_unittest import TestCase


from app.modules.notebooks.models import NotebookSchema, Notebook
from ..file import FileStorageAdapter, NotebookStorageException

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


@pytest.mark.unit
@pytest.mark.notebooks
class NotebookStorageTest(TestCase):

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.adapter = FileStorageAdapter(NotebookSchema(), '/tmp')
        self.nb = Notebook(
            id='foobar',
            name='noo'
        )

    def create_nb_file(self):
        self.fs.create_file('/tmp/{}'.format(self.nb.id), contents=self.adapter.schema.dumps(
            self.nb
        ))

    def test_file_storage_adapter_get(self):
        with pytest.raises(NotebookStorageException):
            self.adapter.get('foobar')
        self.create_nb_file()
        n = self.adapter.get('foobar')
        assert n.id == self.nb.id
        self.fs.remove_object('/tmp/foobar')

    def test_file_storage_adapter_create(self):
        n = Notebook(id=None)

        with pytest.raises(NotebookStorageException):
            self.adapter.create(n)

        self.create_nb_file()
        with pytest.raises(NotebookStorageException):
            # Cannot create with same id
            self.adapter.create(self.nb)

        self.fs.remove_object('/tmp/foobar')
        n = self.adapter.create(self.nb)
        assert n.created_at is not None
        self.fs.remove_object('/tmp/foobar')

    def test_file_storage_adapter_update_partial(self):
        d = {
            'description': 'Fake'
        }
        self.create_nb_file()
        n = self.adapter.save(self.nb.id, d, True)
        assert n.description == 'Fake'
        assert n.updated_at is not None
        self.fs.remove_object('/tmp/foobar')

    def test_file_storage_adapter_delete(self):
        with pytest.raises(NotebookStorageException):
            self.adapter.delete(self.nb.id)
        self.create_nb_file()
        self.adapter.delete(self.nb.id)
        assert self.fs.exists('/tmp/foobar') is False
