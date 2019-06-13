# encoding: utf-8
from urllib.parse import unquote
from marshmallow import ValidationError
# Based on https://stackoverflow.com/questions/14845196/dynamically-constructing-filters-in-sqlalchemy
__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


class FilterParser(object):

    def __init__(self, model_class, sep=';', list_separator=','):
        self.model_class = model_class
        self.sep = sep
        self.list_separator = list_separator

    def parse_filters(self, filters):
        """Parse the user provided filters

        Parameters
        ----------
        filters: list(str)
            List of filters. Each filter uses `sep` as a separator that identifies the LHS, RHS and op

        Returns
        -------
        List of parsed filter representations with op, LHS & RHS
        """
        parsed_filters = []
        for filter_ in filters:
            filter_ = unquote(filter_)
            try:
                key, op, value = filter_.split(self.sep)
                if op == 'in':
                    if value:
                        value = list(value.split(self.list_separator))
                if key is not None and value is not None:
                    parsed_filters.append((
                        op,
                        key,
                        value
                    ))
            except ValueError:
                raise ValidationError('Invalid filter: %s' % filter_)
        return parsed_filters

    def create_filtered_query(self, query, parsed_filters):
        """Filter a given query using provided filters"""

        for [op, key, value] in parsed_filters:
            if not hasattr(self.model_class, key):
                raise ValidationError('Invalid filter specified %s' % key)
            column = getattr(self.model_class, key)

            if op == 'in':
                filt = column.in_(value)
            else:
                try:
                    attr = list(filter(
                        lambda e: hasattr(column, e % op),
                        ['%s', '%s_', '__%s__']
                    ))[0] % op
                except IndexError:
                    raise ValidationError('Invalid filter operator: %s' % op)
                if value == 'null':
                    value = None
                filt = getattr(column, attr)(value)

            query = query.filter(filt)
        return query


class SortFieldsParser:

    def __init__(self, model_class, sep=':'):
        self.model_class = model_class
        self.sep = sep

    def parse_sort_fields(self, sorted_fields):
        """Given a list of fields and sort orders return a parsed representation.

        e.g if input is of the form ['amount:desc', 'name:asc'] we validate the fields
        based on the model class and return vaues
        """
        parsed_sort_fields = list()
        for item in sorted_fields:
            parsed = item.split(self.sep)

            if len(parsed) != 2:
                raise ValidationError('Incorrect argument sent in sort: {}'.format(item))

            field = parsed[0]

            if self.model_class and not hasattr(self.model_class, field):
                raise ValidationError('Unsupported field {}'.format(field))

            order = parsed[1]

            if order not in ['asc', 'desc']:
                raise ValidationError('Sort order should be one of asc or desc')
            parsed_sort_fields.append([field, order])

        return parsed_sort_fields
