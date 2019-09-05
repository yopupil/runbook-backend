# coding: utf8
from marshmallow import fields
from datetime import datetime, timezone

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


class JSDateTime(fields.DateTime):

    def _serialize(self, value, attr, obj):
        utc_dt = value.astimezone(timezone.utc)
        return utc_dt.strftime(
            '%Y-%m-%d %H:%M:%S'
        ) + '.000Z'
