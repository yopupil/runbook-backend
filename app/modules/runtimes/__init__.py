# encoding: utf-8

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


def init_app(app, socketio):

    from .config.loader import runtime_config_loader
    from .namespace import RuntimesNamespace

    # Load runtime configurations
    runtime_config_loader.init_app(app)

    # Add runtimes namespace
    socketio.on_namespace(RuntimesNamespace())
