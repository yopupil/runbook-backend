# encoding: utf-8
import re
from slugify import slugify
from urllib.parse import urlparse

__author__ = 'Tharun Mathew Paul (tmpaul06@gmail.com)'


DATA_TYPE_MAPPING = {
    'string': str,
    'int': int,
    'number': float,
    'bool': bool
}


def typecast_value(value, klass):
    if value is None:
        return value
    if isinstance(value, list):
        return [typecast_value(v, klass) for v in value]
    try:
        if klass == bool:
            return False if (not value or (value and value.lower() == 'false')) else True
        return klass(value)
    except ValueError:
        raise ValueError('Incorrect value {} supplied for type {}'.format(value, klass))


def parse_arg_and_default_value(config):
    """Parse default value from param config"""
    parts = config.split('=')
    if len(parts) == 1:
        return slugify(parts[0], separator='_'), None
    else:
        return slugify(parts[0], separator='_'), parts[1]


def parse_param_config(original_config, param_name='path'):
    """Parse a path or query string config and return type and default value."""
    config = re.sub(r'[<>]', '', original_config)
    data_type = str
    if not len(config):
        raise ValueError('{} config parameter cannot be empty'.format(param_name))
    parts = config.split(':')
    if len(parts) == 1:
        # Check if default value is provided
        query_arg, default_value = parse_arg_and_default_value(parts[0])
    else:
        try:
            data_type = DATA_TYPE_MAPPING[parts[0].strip()]
        except KeyError:
            raise ValueError('Invalid datatype supplied in {} config {}'.format(param_name, parts[0]))
        query_arg, default_value = parse_arg_and_default_value(parts[1].strip())
    if not query_arg:
        raise ValueError('Invalid name supplied for {}'.format(param_name))
    return {
        'dataType': data_type,
        'raw': original_config,
        'arg': query_arg,
        'defaultValue': typecast_value(default_value, data_type)
    }


def get_path_configs(path_template):
    """Given a request uri and path template return the path parameter configurations"""
    path_param_configs = list()
    # First replace all instances of <(...)> with regex capturing braces
    for item in re.findall(r"(<[\w:\d_]+=?[^>]>)", path_template):
        # Get config
        path_param_config = parse_param_config(item)
        path_param_configs.append(path_param_config)
    return path_param_configs


def get_query_configs(query_template):
    query_configs = []
    for item in re.findall(r"(<[\w:\d_]+=?[^>]>)", query_template):
        # Get config
        query_config = parse_param_config(item)
        query_configs.append(query_config)
    return query_configs


def hydrate_path_configs(path_template, path_configs, request_uri):
    """Hydrate the values in config"""
    replaced_path_template = replace_path_template_with_capture_groups(path_template, path_configs)
    pattern = re.compile('/?' + replaced_path_template)
    match = re.search(pattern, request_uri)
    if not match:
        raise ValueError('Invalid path supplied. Path must match format {}'.format(path_template))
    else:
        if len(path_configs):
            curr_group = path_configs[0]['arg']
            try:
                for p in path_configs:
                    curr_group = p['arg']
                    p['value'] = typecast_value(match.group(p['arg']), p['dataType'])
                    if p['value'] is None:
                        p['value'] = p['defaultValue']
            except IndexError:
                # Missing path argument, raise exception
                # This returns 400
                raise ValueError('Missing path argument {}'.format(curr_group))
    return path_configs


def hydrate_query_configs(query_configs, parsed_query_arguments):
    for config in query_configs:
        try:
            default_value = config['defaultValue']
            if default_value is None:
                value = parsed_query_arguments[config['arg']]
            else:
                value = parsed_query_arguments.get(config['arg'], config['defaultValue'])
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
            config['value'] = typecast_value(value, config['dataType'])
        except KeyError:
            raise ValueError('Missing query argument {}'.format(config['arg']))
    return query_configs


def replace_path_template_with_capture_groups(path_template, path_param_configs):
    """Replace path template with regex capture groups to get path param values"""
    path_template_copy = path_template[:]
    for item in path_param_configs:
        path_template_copy = path_template_copy.replace(item['raw'], '(?P<{}>[^/]+)'.format(item['arg']))
    return path_template_copy
