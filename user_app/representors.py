from interview_app.models import Interview
from user_app.models import Profile


def represent_prefrred_districts(instance: Profile):
    if instance.preferred_districts:
        nested_preferred_districts = {}
        for district in instance.preferred_districts.all():
            city = district.city
            province = city.province
            country = province.country
            if country.id not in nested_preferred_districts:
                nested_preferred_districts[country.id] = {'id': country.id, 'name': country.name, 'provinces': []}

            if province.id not in [p['id'] for p in nested_preferred_districts[country.id]['provinces']]:
                nested_preferred_districts[country.id]['provinces'].append(
                    {'id': province.id, 'name': province.name, 'cities': []})

            province_index = [i for i, p in enumerate(nested_preferred_districts[country.id]['provinces']) if
                              p['id'] == province.id][0]

            if city.id not in [c['id'] for c in
                               nested_preferred_districts[country.id]['provinces'][province_index]['cities']]:
                nested_preferred_districts[country.id]['provinces'][province_index]['cities'].append(
                    {'id': city.id, 'name': city.name, 'districts': []})

            city_index = \
                [i for i, c in
                 enumerate(nested_preferred_districts[country.id]['provinces'][province_index]['cities'])
                 if c['id'] == city.id][0]

            nested_preferred_districts[country.id]['provinces'][province_index]['cities'][city_index][
                'districts'].append({
                'id': district.id,
                'name': district.name
            })

        return nested_preferred_districts
    else:
        return []

def represent_districts(instance: Interview):
    if instance.districts:
        nested_preferred_districts = {}
        for district in instance.districts.all():
            city = district.city
            province = city.province
            country = province.country
            if country.id not in nested_preferred_districts:
                nested_preferred_districts[country.id] = {'id': country.id, 'name': country.name, 'provinces': []}

            if province.id not in [p['id'] for p in nested_preferred_districts[country.id]['provinces']]:
                nested_preferred_districts[country.id]['provinces'].append(
                    {'id': province.id, 'name': province.name, 'cities': []})

            province_index = [i for i, p in enumerate(nested_preferred_districts[country.id]['provinces']) if
                              p['id'] == province.id][0]

            if city.id not in [c['id'] for c in
                               nested_preferred_districts[country.id]['provinces'][province_index]['cities']]:
                nested_preferred_districts[country.id]['provinces'][province_index]['cities'].append(
                    {'id': city.id, 'name': city.name, 'districts': []})

            city_index = \
                [i for i, c in
                 enumerate(nested_preferred_districts[country.id]['provinces'][province_index]['cities'])
                 if c['id'] == city.id][0]

            nested_preferred_districts[country.id]['provinces'][province_index]['cities'][city_index][
                'districts'].append({
                'id': district.id,
                'name': district.name
            })

        return nested_preferred_districts
    else:
        return []
