# encoding: utf-8
"""
Common reusable Parameters classes
----------------------------------
"""
import re
from marshmallow import validate

from flask_marshmallow import base_fields
from flask_restplus_patched import Parameters


class PaginationParameters(Parameters):
    """
    Helper Parameters class to reuse pagination.
    """

    limit = base_fields.Integer(
        description="limit a number of items (allowed range is 1-100), default is 10.",
        missing=10,
        validate=validate.Range(min=1, max=100)
    )
    offset = base_fields.Integer(
        description="a number of items to skip, default is 0.",
        missing=0,
        validate=validate.Range(min=0)
    )


class ExtendedPaginationParameters(PaginationParameters):
    """
    Helper parameters that extend base parameters to include sorting and filtering for a given model
    """
    sort = base_fields.List(
        base_fields.String(
            description='List of columns for ordered by in the format {field}:{order} where order is one of asc, desc',
            validate=validate.Regexp(re.compile('(\w+|_):(asc|desc)'))
        )
    )

    filter = base_fields.List(
        base_fields.Str(
            description='List of filters with operators'
        )
    )
