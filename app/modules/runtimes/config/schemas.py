# coding: utf8
from marshmallow import Schema, fields

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


class ClientRuntimeConfigSchema(Schema):
    """The schema for dynamically supplied runtime config"""
    name = fields.Str(required=True)
    image = fields.Str(required=True)
    tag = fields.Str()
    modes = fields.List(fields.Str(), missing=[], validate=lambda x: all([t in ('interactive', 'files', 'endpoints')
                                                                          for t in x]))
    languages = fields.List(fields.Str(), missing=[])


class SourceRuntimeConfigSchema(ClientRuntimeConfigSchema):
    """The schema for runtime provided config."""
    dockerfile_template = fields.Str()
