import ipaddress


def return_range(start_ip, end_ip):
    start = ipaddress.IPv4Address(start_ip)
    end = ipaddress.IPv4Address(end_ip)
    for ip in ipaddress.summarize_address_range(start, end):
        for host in ip:
            yield {
                'ip': str(host),
            }
