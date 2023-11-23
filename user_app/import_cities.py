import os
import json
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "porsline_config.settings")
django.setup()

from user_app.models import Province, City, Country, District
from django.db import transaction


def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


@transaction.atomic
def populate_database(data):
    iran = Country.objects.get(name='ایران')
    for state_name, cities in data.items():
        # Create state
        province = Province.objects.create(name=state_name, country=iran)

        # Create cities for the state
        for city_name in cities:
            city = City.objects.create(name=city_name, province=province)
            for i in range(1, 16):
                District.objects.create(name=f'منطقه {i}', city=city)


if __name__ == "__main__":
    file_path = "/home/ubuntu/state_cities.json"  # Update with the actual path to your JSON file
    data = read_json_file(file_path)
    populate_database(data)
