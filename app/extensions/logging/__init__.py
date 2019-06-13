# encoding: utf-8
"""
Logging adapter for Flask App. Individual services may still use a different
logger. This logger will be used mainly by views
---------------
"""
import logging


__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


class Logging(object):
    """
    This is a helper extension, which adjusts logging configuration for the
    application.
    """

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        Common Flask interface to initialize the logging according to the
        application configuration.
        """
        # We don't need the default Flask's loggers when using our invoke tasks
        # since we set up beautiful colorful loggers globally.
        for handler in list(app.logger.handlers):
            app.logger.removeHandler(handler)
        #app.logger.propagate = True

        if app.debug:
            app.logger.setLevel(logging.DEBUG)
            app.logger.debug('Enabling debug mode!!')
        app.logger.info('Registering logging extension')
