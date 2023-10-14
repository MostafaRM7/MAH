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

# def represent_prefrred_districts(instance: Profile):
#     if instance.preferred_districts:
#         nested_preferred_districts = {}
#         for district in instance.preferred_districts.all():
#             city = district.city
#             province = city.province
#             country = province.country
#             if country.id not in nested_preferred_districts:
#                 nested_preferred_districts[country.id] = {'id': country.id, 'name': country.name, 'provinces': []}
#
#             if province.id not in [p['id'] for p in nested_preferred_districts[country.id]['provinces']]:
#                 nested_preferred_districts[country.id]['provinces'].append(
#                     {'id': province.id, 'name': province.name, 'cities': [], 'all_cities_selected': False})
#
#             province_index = [i for i, p in enumerate(nested_preferred_districts[country.id]['provinces']) if
#                               p['id'] == province.id][0]
#
#             if city.id not in [c['id'] for c in
#                                nested_preferred_districts[country.id]['provinces'][province_index]['cities']]:
#                 nested_preferred_districts[country.id]['provinces'][province_index]['cities'].append(
#                     {'id': city.id, 'name': city.name, 'districts': [], 'all_districts_selected': False})
#
#             city_index = \
#                 [i for i, c in
#                  enumerate(nested_preferred_districts[country.id]['provinces'][province_index]['cities'])
#                  if c['id'] == city.id][0]
#
#             nested_preferred_districts[country.id]['provinces'][province_index]['cities'][city_index][
#                 'districts'].append({
#                 'id': district.id,
#                 'name': district.name
#             })
#
#         # Check if all districts are selected for each city
#         for country_data in nested_preferred_districts.values():
#             for province_data in country_data['provinces']:
#                 for city_data in province_data['cities']:
#                     if len(city_data['districts']) == len(
#                             [d for d in city_data['districts'] if d['all_districts_selected']]):
#                         city_data['all_districts_selected'] = True
#
#         return nested_preferred_districts
#     else:
#         return []
