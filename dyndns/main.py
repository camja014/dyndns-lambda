import re
from pprint import pprint

from ddns import dyndns, duckdns
from error import RequestInvalidError

ROUTES = {
    r'^/update$': duckdns.update,
    r'^/nic/update$': dyndns.update,
    r'^/v3/update$': dyndns.update,
}


def request_handler(event, context):
    try:
        method = event['httpMethod']
        if method.upper() != 'GET':
            raise RequestInvalidError(400, 'method_invalid')

        path = event['path']
        params = event['queryStringParameters']
        headers = event['headers']

        response = {
            'statusCode': 400,
            'body': 'bad_request',
        }

        for route, handler in ROUTES.items():
            if re.match(route, path):
                response = handler(
                    path=path,
                    query_params=params,
                    headers=headers
                )

        return response

    except RequestInvalidError as e:
        return {'statusCode': e.status_code, 'body': e.message}

    except KeyError:
        return {'statusCode': 400, 'body': 'request_invalid'}

    except RuntimeError:
        return {'statusCode': 500, 'body': 'server_error'}


if __name__ == '__main__':
    _response = request_handler({
        'path': '/update',
        'queryStringParameters': {
            'ip': '73.216.59.248',
            'domains': 'duckdns',
            'token': 'i5RSCjRQXUvvCVVdJs7fK3Twj38m2hReV3bZoyKvQI76h4wC',
        },
        'headers': {

        },
        'httpMethod': 'GET',
    }, None)

    pprint(_response)

    import base64

    _response = request_handler({
        'path': '/v3/update',
        'queryStringParameters': {
            'myip': '73.216.59.248',
            'hostname': 'dyndns',
        },
        'headers': {
            'Authorization': 'Basic ' + base64.b64encode(
                b'none:i5RSCjRQXUvvCVVdJs7fK3Twj38m2hReV3bZoyKvQI76h4wC'
            ).decode('ascii')
        },
        'httpMethod': 'GET',
    }, None)

    pprint(_response)
