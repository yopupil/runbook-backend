# coding: utf8
from datetime import datetime

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


class Notebook:
    """A model representing a notebook

    Parameters
    ----------
    id: str
        The id of the notebook

    name: str
        The name of the notebook

    description: str
        The description of the notebook

    created_at: datetime
        The datetime corresponding to creation point of notebook

    updated_at: datetime
        The datetime corresponding to the point where notebook was last updated at.
    """
    def __init__(self, id=None, name=None, description='',
                 created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at

    def merge(self, partial_dict):
        """Merge partial changes onto self"""
        for key in ['name', 'description', 'updated_at']:
            setattr(self, key, partial_dict.get(key, getattr(self, key)))
