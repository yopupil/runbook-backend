"""
A facade for the actual underlying session. This module exposes a couple of
variables like current_user, current_organization etc. These are local proxies
to the underlying session objects.

http://werkzeug.pocoo.org/docs/0.14/local/

Inspired by: https://github.com/maxcountryman/flask-login

"""
from flask import current_app, session, g
from werkzeug.local import LocalProxy

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


def ensure_auth_service(app):
    """Ensure that app has a login manager defined."""
    if not hasattr(app, 'auth_service'):
        raise RuntimeError('Application must have a authentication service defined and accessible as app.auth_service')


def _get_user():
    """Return the current user on the request context."""
    # login_manager will load the user on request context once.
    # any subsequent calls will result in the same user being
    # returned to avoid roundtrip calls.
    ensure_auth_service(current_app)
    return current_app.auth_service.load_current_user(session, context=g)


def _get_organization():
    """Return the current organization that user is scoped to."""
    ensure_auth_service(current_app)
    return current_app.auth_service.load_current_organization(session, context=g)


def _get_user_id():
    """Return the current user on the request context."""
    # login_manager will load the user on request context once.
    # any subsequent calls will result in the same user being
    # returned to avoid roundtrip calls.
    ensure_auth_service(current_app)
    return current_app.auth_service.load_current_user_id(session, context=g)


def _get_organization_id():
    """Return the current organization that user is scoped to."""
    ensure_auth_service(current_app)
    return current_app.auth_service.load_current_organization_id(session, context=g)


###################################
#
# Usable exports
#
###################################
# https://stackoverflow.com/questions/3203286/how-to-create-a-read-only-class-property-in-python
class LocalContextMeta(type):
    @staticmethod
    def proxy_resolve(obj):
        if isinstance(obj, LocalProxy):
            return obj._get_current_object()
        return obj

    @property
    def current_user(cls):
        return LocalContextMeta.proxy_resolve(cls._current_user)

    @property
    def current_user_id(cls):
        return LocalContextMeta.proxy_resolve(cls._current_user_id)

    @property
    def current_organization(cls):
        return LocalContextMeta.proxy_resolve(cls._current_organization)

    @property
    def current_organization_id(cls):
        return LocalContextMeta.proxy_resolve(cls._current_organization_id)


class AuthContext(object, metaclass=LocalContextMeta):
    _current_user = LocalProxy(_get_user)
    _current_organization = LocalProxy(_get_organization)
    _current_user_id = LocalProxy(_get_user_id)
    _current_organization_id = LocalProxy(_get_organization_id)
