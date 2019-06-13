# encoding: utf-8
"""
Extended Api Namespace implementation with an application-specific helpers
--------------------------------------------------------------------------
"""
from contextlib import contextmanager
from functools import wraps
import logging

import flask_marshmallow
from marshmallow import ValidationError
import sqlalchemy
from sqlalchemy import asc, desc

from flask_restplus_patched import Namespace as BaseNamespace
from flask_restplus._http import HTTPStatus

from . import http_exceptions
from .custom_field_parsers import SortFieldsParser, FilterParser
from .webargs_parser import CustomWebargsParser


log = logging.getLogger(__name__)


class Namespace(BaseNamespace):
    """
    Having app-specific handlers here.
    """

    WEBARGS_PARSER = CustomWebargsParser()

    def wrap_resolver_with_api_abort(self, resolver, not_found_template):
        """Wrap model resolvers with custom API abort method.

        Regular abort using flask will return the message that tells the user to double
        check the URL & path. But in reality the 404 occurs because the resource is not
        available. Therefore we wrap resolvers with custom method so that it uses api_abort
        instead

        Arguments:
            resolver(method) - The resolver method
            not_found_template(method) - A method that provides the message to use.
        """
        def wrapped_resolver(kwargs):
            m = resolver(kwargs)
            if m is None:
                return http_exceptions.api_abort(404, message=not_found_template(kwargs))
            return m
        return wrapped_resolver

    def resolve_object_by_model(self, model, object_arg_name, identity_arg_names=None, resolver=None):
        """
        A helper decorator to resolve DB record instance by id.

        Arguments:
            model (type) - a Flask-SQLAlchemy model class with
                ``query.get_or_404`` method
            object_arg_name (str) - argument name for a resolved object
            identity_arg_names (tuple) - a list of argument names holding an
                object identity, by default it will be auto-generated as
                ``%(object_arg_name)s_id``.
            resolver (method) - an optional method that performs custom resolution

        Example:
        >>> @namespace.resolve_object_by_model(User, 'user')
        ... def get_user_by_id(user):
        ...     return user
        >>> get_user_by_id(user_id=3)
        <User(id=3, ...)>

        >>> @namespace.resolve_object_by_model(MyModel, 'my_model', ('user_id', 'model_name'))
        ... def get_object_by_two_primary_keys(my_model):
        ...     return my_model
        >>> get_object_by_two_primary_keys(user_id=3, model_name="test")
        <MyModel(user_id=3, name="test", ...)>
        """
        if identity_arg_names is None:
            identity_arg_names = ('%s_id' % object_arg_name, )
        elif not isinstance(identity_arg_names, (list, tuple)):
            identity_arg_names = (identity_arg_names, )

        not_found_template = lambda kwargs: 'Cannot find {} with {}'.format(
            object_arg_name,
            ','.join(['{}={}'.format(k, v) for k, v in kwargs.items()])
        )

        def model_resolver(kwargs):
            m_args = [kwargs.pop(identity_arg_name) for identity_arg_name in identity_arg_names]
            m = model.query.get(m_args)
            return m

        if resolver is None:
            resolver = model_resolver
        return self.resolve_object(
            object_arg_name,
            resolver=self.wrap_resolver_with_api_abort(resolver, not_found_template)
        )

    def model(self, name=None, model=None, **kwargs):
        # pylint: disable=arguments-differ
        """
        A decorator which registers a model (aka schema / definition).

        This extended implementation auto-generates a name for
        ``Flask-Marshmallow.Schema``-based instances by using a class name
        with stripped off `Schema` prefix.
        """
        if isinstance(model, flask_marshmallow.Schema) and not name:
            name = model.__class__.__name__
            if name.endswith('Schema'):
                name = name[:-len('Schema')]
        return super(Namespace, self).model(name=name, model=model, **kwargs)

    def _register_access_restriction_decorator(self, func, decorator_to_register):
        # pylint: disable=invalid-name
        """
        Helper function to register decorator to function to perform checks
        in options method
        """
        if not hasattr(func, '_access_restriction_decorators'):
            func._access_restriction_decorators = []  # pylint: disable=protected-access
        func._access_restriction_decorators.append(decorator_to_register)  # pylint: disable=protected-access

    def paginate(self, parameters=None, locations=None, model=None, default_sort=None):
        """
        Endpoint parameters registration decorator special for pagination.
        If ``parameters`` is not provided default PaginationParameters will be
        used.

        Also, any custom Parameters can be used, but it needs to have ``limit`` and ``offset`` fields

        Parameters
        ----------
        parameters: Parameters
            The parameters to use, if not provided defaults to basic PaginationParameters without sort and filter

        locations: tuple
            Tuple of parameter locations to look for

        model: object
            SQLAlchemy model

        default_sort: list, optional
            An optional list that acts as default sort if no sort parameter is provided
        """
        if not parameters:
            # Use default parameters if None specified
            from app.extensions.api.parameters import PaginationParameters
            parameters = PaginationParameters()

        if not all(
            mandatory in parameters.declared_fields
            for mandatory in ('limit', 'offset')
        ):
            raise AttributeError(
                '`limit` and `offset` fields must be in Parameter passed to `paginate()`'
            )

        if any(
            field in parameters.declared_fields
            for field in ['sort', 'filter']
        ) and model is None:
            raise AttributeError('For `sort` and `filter` fields supported by parameters a model is required')

        def decorator(func):
            @wraps(func)
            def wrapper(self_, parameters_args, *args, **kwargs):
                queryset = func(self_, parameters_args, *args, **kwargs)
                # For sorting and filtering, we need model
                sort_fields = parameters_args.get('sort', default_sort or [])
                filter_fields = parameters_args.get('filter', [])

                try:
                    if len(filter_fields):
                        filter_parser = FilterParser(model)

                        # Get filtered query set
                        queryset = filter_parser.create_filtered_query(queryset, filter_parser.parse_filters(
                            parameters_args['filter']))

                    if len(sort_fields):
                        sort_fields = SortFieldsParser(model).parse_sort_fields(sort_fields)

                        if sort_fields and len(sort_fields):
                            queryset = queryset.order_by(
                                *[
                                    desc(field) if order == 'desc' else asc(field) for field, order in sort_fields
                                ]
                            )
                except ValidationError as e:
                    return http_exceptions.api_abort(400, str(e))

                # Get count
                total_count = queryset.count()
                return (
                    queryset
                        .offset(parameters_args['offset'])
                        .limit(parameters_args['limit']),
                    HTTPStatus.OK,
                    {'X-Total-Count': total_count}
                )
            return self.parameters(parameters, locations)(wrapper)
        return decorator

    @contextmanager
    def commit_or_abort(self, session, default_error_message="The operation failed to complete"):
        """
        Context manager to simplify a workflow in resources

        Args:
            session: db.session instance
            default_error_message: Custom error message

        Exampple:
        >>> with api.commit_or_abort(db.session):
        ...     team = Team(**args)
        ...     db.session.add(team)
        ...     return team
        """
        try:
            yield session
            session.commit()
        except ValueError as exception:
            session.rollback()
            log.info("Database transaction was rolled back due to: %r", exception)
            http_exceptions.abort(code=HTTPStatus.CONFLICT, message=str(exception))
        except ValidationError as exception:
            log.info("Invalid patch operation attempted")
            http_exceptions.abort(code=HTTPStatus.UNPROCESSABLE_ENTITY, message=str(exception))
        except sqlalchemy.exc.IntegrityError as exception:
            session.rollback()
            log.info("Database transaction was rolled back due to: %r", exception)
            http_exceptions.abort(
                code=HTTPStatus.CONFLICT,
                message=default_error_message
            )
