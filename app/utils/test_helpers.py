from werkzeug.http import parse_cookie

__author__ = 'Rahul Kumar Verma (rahul.kumar@bipiventures.com)'


def check_cookie(response, name, value):
    # Checks for existence of a cookie and verifies the value of it.
    cookies = response.headers.getlist('Set-Cookie')
    for cookie in cookies:
        c_key, c_value = list(parse_cookie(cookie).items())[0]
        if c_key == name:
            assert c_value == value
            return
    # Cookie not found
    assert False
