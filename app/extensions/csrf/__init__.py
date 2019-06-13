from flask import request, redirect, url_for, jsonify, make_response
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


def init_app(app):
    """Initialize CSRF Error handling"""

    csrf_protect = CSRFProtect()

    # Initialize CSRF extension
    csrf_protect.init_app(app)

    app.logger.info('Registering CSRF extension')

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        # Log the exception so that we can trace the source of failure
        app.logger.error(e)
        error_message = 'There is a problem with your CSRF token. Make sure ' \
                        'cookies are enabled in your browser, and try ' \
                        'reloading this page.'

        # If the request involves an API endpoint, redirect to login page via
        # issuing 401
        if 'api/' in request.url:
            return make_response(jsonify(message=error_message), 401)
        else:
            # Redirect to login page via app.LOGIN_URI
            return redirect(url_for(app.config['LOGIN_URI']))
