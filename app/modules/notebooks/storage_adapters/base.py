# coding: utf8
import abc

from app.modules.notebooks.models import Notebook

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


class INotebookStoreAdapter(metaclass=abc.ABCMeta):

    class NotebookStorageException(Exception):
        pass

    def __init__(self, schema):
        """
        Parameters
        ----------
        schema: Schema
            A marshmallow schema or equivalent that serializes and deserializes
            notebook data into the preferred medium.
        """
        self.schema = schema

    @abc.abstractmethod
    def get(self, notebook_id) -> Notebook:
        """Get a notebook by its id."""
        pass

    @abc.abstractmethod
    def create(self, payload: Notebook) -> Notebook:
        """Create a new notebook.

        Parameters
        ----------
        payload: dict
            Can be serialized into string or binary

        Returns
        -------
        created notebook
        """
        pass

    @abc.abstractmethod
    def save(self, notebook_id, payload, partial=True) -> Notebook:
        """Save a part of the notebook

        Parameters
        ----------
        notebook_id: str
            The id of the notebook

        payload: dict
            Can be serialized into string or binary

        partial: bool, optional
            If true, the payload is partial. Do a refetch and merge before save.

        Returns
        -------
        updated notebook
        """

    @abc.abstractmethod
    def delete(self, notebook_id):
        """Delete a notebook by its id"""
        pass

