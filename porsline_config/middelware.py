import pycountry
from ipware import get_client_ip
from django.http import HttpResponseForbidden


class BlockIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        client_ip, _ = get_client_ip(request)
        if client_ip:
            try:
                country_code = pycountry.countries.get(alpha_2='IR').alpha_2  # Change 'IR' to the desired country code
                ip_country_code = pycountry.countries.get(alpha_2=client_ip.upper()).alpha_2
                if ip_country_code != country_code:
                    return HttpResponseForbidden("<h1>Forbidden</h1>")
            except (AttributeError, KeyError):
                pass  # Country code not found for the client IP
        return self.get_response(request)
