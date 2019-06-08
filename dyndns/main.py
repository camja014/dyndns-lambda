import re

from ddns import duckdns, dyndns
from utils.error import RequestInvalidError, AuthenticationFailedError

DUCK_DNS_ROUTE_PTRN = re.compile(r'^/update$')
DYN_DNS_LEG_ROUTE_PTRN = re.compile(r'^/nic/update$')
DYN_DNS_ROUTE_PTRN = re.compile(r'^/v3/update$')


def request_handler(event, context):
    try:
        method = event['httpMethod']
        if method.upper() != 'GET':
            raise RequestInvalidError(400, 'method_invalid')

        path = event['path']
        update_args = {
            'path': event['path'],
            'query_params': event['queryStringParameters'],
            'headers': event['headers'],
        }

        response = None
        if re.match(DUCK_DNS_ROUTE_PTRN, path):
            duckdns.update(**update_args)
        if re.match(DYN_DNS_LEG_ROUTE_PTRN, path) or re.match(
                DYN_DNS_ROUTE_PTRN, path):
            dyndns.update(**update_args)
        else:
            response = {
                'statusCode': 400,
                'body': 'bad_request',
            }

        return response

    except RequestInvalidError as e:
        return {'statusCode': e.status_code, 'body': e.message}

    except AuthenticationFailedError as e:
        return {'statusCode': 401, 'body': e.message}

    except KeyError:
        return {'statusCode': 400, 'body': 'request_invalid'}

    except RuntimeError:
        return {'statusCode': 500, 'body': 'server_error'}
