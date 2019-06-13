from .decorators import authenticate_route, authenticate_api, permissions_required
from .services import BaseAuthService
from .context import AuthContext


def init_app(app):
    """Initialize auth extensions"""
    # pylint: disable=unused-argument
    app.logger.info('Registering auth extension')
    pass
