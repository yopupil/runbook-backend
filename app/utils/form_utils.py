#http://flask.pocoo.org/snippets/63/
from urllib.parse import urlparse, urljoin
from flask import request, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField

from .flask_utils import is_safe_url


def get_redirect_target():
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target, request.host_url):
            return target


class RedirectForm(FlaskForm):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = request.args.get('next')

    def redirect(self, endpoint='index', **values):
        if is_safe_url(self.next.data, request.host_url):
            return redirect(self.next.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))


class ConfirmationForm(FlaskForm):
    """User edit form"""

    def __init__(self, confirmation_message='Are you sure',
                 confirm_text='Yes', confirm_cancel='No'):
        super().__init__()
        self.confirmation_message = confirmation_message
        self.confirm_text = confirm_text
        self.confirm_cancel = confirm_cancel

    yes = StringField('yes')
    no = StringField('no')

