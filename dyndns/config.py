import os

import boto3 as boto3


def get_config(token):
    region_name = os.getenv('AWS_REGION', 'us-east-1')
    table_name = os.getenv('DYNAMODB_TABLE_NAME', 'DynDNSConfig')

    dynamodb = boto3.resource('dynamodb', region_name=region_name)
    table = dynamodb.Table(table_name)

    return table.get_item(Key={'Token': token})['Item']
