import base64
from ipaddress import ip_address

from config import CONFIG
from error import AuthenticationFailedError
from route53 import update_records


def update(**kwargs):
    query_params = kwargs.get('query_params')
    headers = kwargs.get('headers')
    auth_token = _parse_auth(headers)
    domain, zone_id = _auth(auth_token)
    updates = _get_host_updates(query_params)
    changed = update_records(updates, zone_id, domain)

    if changed:
        body = 'good'
    else:
        body = 'nochg'

    return {
        'statusCode': 200,
        'body': body,
    }


def _auth(auth_token):
    try:
        zone_id = CONFIG['zone'][auth_token]['zone_id']
        domain = CONFIG['zone'][auth_token]['domain']
    except KeyError:
        raise AuthenticationFailedError('bad')
    return domain, zone_id


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
