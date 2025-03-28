import geoip2.database
import geoip2.errors
from django.http import HttpResponseForbidden, HttpRequest


class BlockIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.db = geoip2.database.Reader('GeoLite2-City.mmdb')
        # self.country_reader = geoip2.database.Reader('GeoLite2-Country.mmdb')

    def __call__(self, request: HttpRequest):
        # Get the client's IP address
        client_ip = self.get_client_ip(request)

        request.location = self.get_user_location(client_ip)

        # Check if the IP address belongs to Iran (country code 'IR')
        if self.is_iranian_ip(client_ip):
            return self.get_response(request)

        # If the IP address is not from Iran, deny access
        return HttpResponseForbidden(f"We are sorry, access denied from your current location: {self.get_user_location(client_ip).get('country')}, {self.get_user_location(client_ip).get('city')}.")

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def is_iranian_ip(self, ip):
        try:
            response = self.db.city(ip)
            return response.country.iso_code == 'IR'
        except geoip2.errors.AddressNotFoundError:
            return False

    def get_user_location(self, ip):
        try:
            response = self.db.city(ip)
            return {
                'city': response.city.name,
                'country': response.country.name,
                'country_iso_code': response.country.iso_code,
            }
        except geoip2.errors.AddressNotFoundError:
            return None
