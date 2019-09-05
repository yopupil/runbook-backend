# coding: utf8
import os

from .base import INotebookStoreAdapter

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'

NotebookStorageException = INotebookStoreAdapter.NotebookStorageException


class FileStorageAdapter(INotebookStoreAdapter):
    """A storage adapter that writes notebooks to file"""
    def __init__(self, schema, notebooks_dir):
        super().__init__(schema)
        self.notebooks_dir = notebooks_dir

    def _get_file_path(self, notebook_id):
        return os.path.join(self.notebooks_dir, notebook_id)

    def create(self, payload):
        """Create a new notebook on disk"""
        if 'id' not in payload:
            raise NotebookStorageException('A notebook must have an id to be saved.')
        file_path = self._get_file_path(payload['id'])
        if os.path.exists(file_path):
            raise NotebookStorageException('Another notebook already exists with the same id.')
        else:
            with open(file_path, 'w') as f:
                f.write(self.schema.dumps(payload))

    def get(self, notebook_id):
        """Get a notebook by its id"""
        file_path = self._get_file_path(notebook_id)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return self.schema.loads(f.read())
        else:
            raise NotebookStorageException('Cannot find a notebook with id {}'.format(notebook_id))

    def save(self, notebook_id, payload, partial=True):
        """Save a notebook"""
        if partial is True:
            doc = self.get(notebook_id)
            # The model must support merging
            if hasattr(doc, 'merge'):
                doc.merge(payload)
            else:
                doc_dict = self.schema.dump(doc)
                doc = self.schema.load({**doc_dict, **payload})
        else:
            if isinstance(payload, dict):
                doc = self.schema.load(payload)
            else:
                doc = payload
        file_path = self._get_file_path(notebook_id)
        with open(file_path, 'w') as f:
            f.write(self.schema.dumps(doc))

    def delete(self, notebook_id):
        """Delete notebook"""
        file_path = self._get_file_path(notebook_id)
        if os.path.exists(file_path):
            os.unlink(file_path)
        else:
            raise NotebookStorageException('Cannot find a notebook with id {}'.format(notebook_id))