from ipaddress import ip_address

from config import get_config
from route53 import update_records
from utils.error import AuthenticationFailedError, RequestInvalidError


def update(**kwargs):
    query_params = kwargs.get('query_params')
    # authenticate the given token against the configure token
    config = _auth(query_params)
    # get IP addresses to update
    ip, ipv6 = _parse_ip_addrs(query_params)
    # create list of hostname/ip pairs that will be updated
    updates = _create_updates_list(ip, ipv6, query_params)
    # perform dns update
    zone_id = config['ZoneID']
    domain = config['Domain']
    ttl = int(config.get('TTL', 60))
    update_records(updates, zone_id, domain, ttl=ttl)

    return {
        'statusCode': 200,
        'body': 'OK'
    }


def _parse_ip_addrs(query_params):
    ip = ip_address(query_params['ip'])
    ipv6 = None
    if 'ipv6' in query_params:
        ipv6 = ip_address(query_params['ipv6'])
        # if both ip and ipv6 are defined, ip must be v4, and ipv6 must be v6
        if (ipv6.version != 6) and (ip.version == 6):
            raise RequestInvalidError()
    return ip, ipv6


def _create_updates_list(ip, ipv6, query_params):
    hostnames = query_params['domains'].split(',')
    updates = [(host, ip) for host in hostnames]
    if ipv6:
        updates += [(host, ipv6) for host in hostnames]
    return updates


def _auth(query_params):
    token = query_params['token']
    config = get_config(token)
    if not config:
        raise AuthenticationFailedError('KO')
    return config
