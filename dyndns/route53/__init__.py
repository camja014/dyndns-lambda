import boto3 as boto3

from config import CONFIG


def update_records(hosts, zone_id, domain):
    route53 = _get_client()
    update_hosts = _get_update_docs(domain, hosts)
    response = _update_record_sets(route53, update_hosts, zone_id)
    return True if response['ChangeInfo']['Status'] == 'INSYNC' else False


def _get_update_docs(domain, hosts):
    update_hosts = []
    for host, ip_addr in hosts:
        record_type = _get_record_type(ip_addr)
        name = f'{host}.{domain}'
        record = _get_update_doc(name, record_type, 0, str(ip_addr))
        update_hosts.append(record)
    return update_hosts


def _update_record_sets(route53, update_hosts, zone_id):
    return route53.change_resource_record_sets(
        HostedZoneId=zone_id,
        ChangeBatch={
            'Changes': update_hosts
        }
    )


def _get_client():
    route53 = boto3.client(
        'route53',
        aws_access_key_id=CONFIG['aws_access_key_id'],
        aws_secret_access_key=CONFIG['aws_secret_access_key'],
    )
    return route53


def _get_record_type(ip_addr):
    if ip_addr.version == 4:
        record_type = 'A'
    elif ip_addr.version == 6:
        record_type = 'AAAA'
    else:
        raise TypeError()
    return record_type


def _get_update_doc(name, record_type, ttl, value):
    return {
        'Action': 'UPSERT',
        'ResourceRecordSet': {
            'Name': name,
            'Type': record_type,
            'TTL': ttl,
            'ResourceRecords': [
                {
                    'Value': value,
                }
            ],
        }
    }
