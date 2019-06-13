from urllib.parse import urlparse, urljoin
from flask.globals import _app_ctx_stack, _request_ctx_stack
from werkzeug.exceptions import NotFound
from werkzeug.urls import url_parse

__author__ = 'Tharun M Paul (tmpaul06@gmail.com)'


# http://flask.pocoo.org/snippets/62/
def is_safe_url(target, host_url):
    ref_url = urlparse(host_url)
    test_url = urlparse(urljoin(host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


# https://stackoverflow.com/questions/19631335/reverting-a-url-in-flask-to-the-endpoint-arguments
def get_endpoint_from_url(url, method=None):
    """Given an URL and optional method return the flask endpoint.

    Parameters
    ----------
    url: str
        The url to fetch endpoint for

    method: str, optional
        The HTTP method to limit to.

    Returns
    -------
    result: tuple
        A tuple, with the first element being the endpoint name and the second a dictionary with the arguments.

    Raises
    ------
    werkzeug.exceptions.NotFound if an endpoint cannot be found
    RunTimeError if a request context is not available
    """
    appctx = _app_ctx_stack.top
    reqctx = _request_ctx_stack.top
    if appctx is None:
        raise RuntimeError('Attempted to match a URL without the '
                           'application context being pushed. This has to be '
                           'executed when application context is available.')

    if reqctx is not None:
        url_adapter = reqctx.url_adapter
    else:
        url_adapter = appctx.url_adapter
        if url_adapter is None:
            raise RuntimeError('Application was not able to create a URL '
                               'adapter for request independent URL matching. '
                               'You might be able to fix this by setting '
                               'the SERVER_NAME config variable.')
    parsed_url = url_parse(url)
    if parsed_url.netloc is not "" and parsed_url.netloc != url_adapter.server_name:
        raise NotFound('Cannot find route for url')
    return url_adapter.match(parsed_url.path, method)
