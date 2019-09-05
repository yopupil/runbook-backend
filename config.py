# pylint: disable=too-few-public-methods,invalid-name,missing-docstring
import os
import redis

__author__ = 'Tharun M Paul (tmpaul06@gmail.com)'


class BaseConfig(object):
    SECRET_KEY = 'this-really-needs-to-be-changed'

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    # SQLITE
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % (os.path.join(PROJECT_ROOT, 'aura.db'))

    DEBUG = False

    # These are required by several other extensions. Therefore make sure that auth endpoints
    # point to these URIs correctly
    LOGIN_URL = '/auth/login'
    LOGOUT_URL = '/auth/logout'

    ENABLED_MODULES = (
      'api',
      'notebooks'
    )

    STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    CSRF_ENABLED = True


class ProductionConfig(BaseConfig):
    # *****************************
    # Environment specific settings
    # *****************************

    # DO NOT use "DEBUG = True" in production environments
    DEBUG = False

    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_NAME = 'aura.sid'
    ORGANIZATION_COOKIE_NAME = 'aura.oid'
    CSRF_TOKEN_COOKIE_NAME = 'csrf_token'

    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids a SQLAlchemy Warning

    # Application settings
    # Flask settings
    CSRF_ENABLED = True
    # 20 MB max file size upload
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024

    #
    # 60 minutes session
    PERMANENT_SESSION_LIFETIME = 60 * 60
    SESSION_REDIS = redis.Redis('redis-session')
    SESSION_TYPE = 'redis'
    WTF_CSRF_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    WTF_CSRF_TIME_LIMIT = None


class DevelopmentConfig(BaseConfig):
    # *****************************
    # Environment specific settings
    # *****************************
    DEBUG = True

    SECRET_KEY = 'This is an UNSECURE Secret. CHANGE THIS for production environments.'
    SESSION_COOKIE_NAME = 'aura.sid'
    ORGANIZATION_COOKIE_NAME = 'aura.oid'
    CSRF_TOKEN_COOKIE_NAME = 'csrf_token'
    ENABLE_SWAGGER_API = '/'

    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids a SQLAlchemy Warning

    # Application settings
    # Flask settings
    CSRF_ENABLED = True
    # 20 MB max file size upload
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024

    # 15 minute session
    PERMANENT_SESSION_LIFETIME = 15 * 60
    SESSION_REDIS = redis.Redis('redis')
    SESSION_TYPE = 'redis'
    WTF_CSRF_SECRET_KEY = 'my super secret wtf key'
    WTF_CSRF_TIME_LIMIT = None


class TestingConfig(BaseConfig):

    BCRYPT_LOG_ROUNDS = 4

    TESTING = True
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    # SECRET_KEY = 'My dummy secret key'
    SQLALCHEMY_ECHO = False
    SECRET_KEY = 'not so secret test key'
    SESSION_COOKIE_NAME = 'aura.sid'
    ORGANIZATION_COOKIE_NAME = 'aura.oid'
    CSRF_TOKEN_COOKIE_NAME = 'csrf_token'

    SESSION_TYPE = 'filesystem'


class CITestingConfig(BaseConfig):
    BCRYPT_LOG_ROUNDS = 4

    TESTING = True
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    # SECRET_KEY = 'My dummy secret key'
    SQLALCHEMY_ECHO = False
    SECRET_KEY = 'not so secret test key'
    SESSION_COOKIE_NAME = 'aura.sid'
    ORGANIZATION_COOKIE_NAME = 'aura.oid'
    CSRF_TOKEN_COOKIE_NAME = 'csrf_token'

    SESSION_TYPE = 'filesystem'
