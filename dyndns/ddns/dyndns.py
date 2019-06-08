import base64
from ipaddress import ip_address

from config import get_config
from utils.error import AuthenticationFailedError
from route53 import update_records


def update(**kwargs):
    query_params = kwargs.get('query_params')
    headers = kwargs.get('headers')
    auth_token = _parse_auth(headers)
    config = _auth(auth_token)
    updates = _get_host_updates(query_params)

    zone_id = config['ZoneID']
    domain = config['Domain']
    ttl = int(config.get('TTL', 60))
    changed = update_records(updates, zone_id, domain, ttl=ttl)

    if changed:
        body = 'good'
    else:
        body = 'nochg'

    return {
        'statusCode': 200,
        'body': body,
    }


def _auth(auth_token):
    config = get_config(auth_token)
    if not config:
        raise AuthenticationFailedError('bad')
    return config


def _get_host_updates(query_params):
    hostnames = query_params['hostname'].split(',')
    ip = ip_address(query_params['myip'])
    updates = [(host, ip) for host in hostnames]
    return updates


def _parse_auth(headers):
    auth_header = headers['Authorization']
    auth_type, auth_str = auth_header.split()

    if auth_type != 'Basic':
        raise AuthenticationFailedError('bad')

    auth_str = base64.b64decode(auth_str).decode('ascii')
    auth_user, auth_token = auth_str.split(':')

    if auth_user != 'none':
        raise AuthenticationFailedError('bad')

    return auth_token
