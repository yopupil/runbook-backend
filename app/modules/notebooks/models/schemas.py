# coding: utf8
from marshmallow import Schema, fields, post_load

from app.utils import JSDateTime
from .notebook import Notebook

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


class NotebookSchema(Schema):
    """Marshmallow schema for serialization and deserialization"""
    id = fields.String(required=True)
    name = fields.String(required=True)
    description = fields.String(missing='')
    created_at = JSDateTime('iso8601', allow_none=True)
    updated_at = JSDateTime('iso8601', allow_none=True)

    @post_load
    def make_notebook(self, data):
        return Notebook(**data)
