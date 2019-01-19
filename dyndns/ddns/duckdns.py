from ipaddress import ip_address

from config import CONFIG
from error import AuthenticationFailedError, RequestInvalidError
from route53 import update_records


def update(**kwargs):
    query_params = kwargs.get('query_params')

    # authenticate the given token against the configure token
    try:
        token = query_params['token']
        zone_id = CONFIG['zone'][token]['zone_id']
    except KeyError:
        raise AuthenticationFailedError('KO')

    # get domain from config
    domain = CONFIG['zone'][token]['domain']

    # get IP addresses to update
    ip = ip_address(query_params['ip'])
    ipv6 = None
    if 'ipv6' in query_params:
        ipv6 = ip_address(query_params['ipv6'])
        # if both ip and ipv6 are defined, ip must be v4, and ipv6 must be v6
        if (ipv6.version != 6) and (ip.version == 6):
            raise RequestInvalidError()

    hostnames = query_params['domains'].split(',')
    updates = [(host, ip) for host in hostnames]

    if ipv6:
        updates += [(host, ipv6) for host in hostnames]

    update_records(updates, zone_id, domain)

    return {
        'statusCode': 200,
        'body': 'OK'
    }
