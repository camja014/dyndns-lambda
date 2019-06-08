import boto3


def update_records(hosts, zone_id, domain, ttl=60):
    update_hosts = _get_update_docs(domain, hosts, ttl)
    response = _update_record_sets(update_hosts, zone_id)
    return True if response['ChangeInfo']['Status'] == 'INSYNC' else False


def _get_update_docs(domain, hosts, ttl):
    update_hosts = []
    for host, ip_addr in hosts:
        record_type = _get_record_type(ip_addr)
        name = f'{host}.{domain}'
        record = _get_update_doc(name, record_type, ttl, str(ip_addr))
        update_hosts.append(record)
    return update_hosts


def _update_record_sets(update_hosts, zone_id):
    route53 = boto3.client('route53')
    return route53.change_resource_record_sets(
        HostedZoneId=zone_id,
        ChangeBatch={
            'Changes': update_hosts
        }
    )


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
