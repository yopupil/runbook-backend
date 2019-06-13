import abc

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


class BaseAuthService(metaclass=abc.ABCMeta):
    """A class representing operations on flask session that abstract away authentication context"""

    @staticmethod
    @abc.abstractmethod
    def load_current_user(session, context=None):
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def load_current_user_id(session, context=None):
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def load_current_organization(session, context=None):
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def load_current_organization_id(session, context=None):
        raise NotImplementedError()
