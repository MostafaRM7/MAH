from user_app.models import Profile


def validate_user_info(user: Profile, for_interview):
    try:
        if user.wallet is None:
            return False
    except:
        return False
    if user.first_name is None or user.first_name == '':
        return False
    if user.last_name is None or user.last_name == '':
        return False
    if user.email is None or user.email == '':
        return False
    if for_interview:
        if user.preferred_districts.all().exists() is False:
            return False
    if user.province is None:
        return False
    if user.nationality is None:
        return False
    if user.gender is None or user.gender == '':
        return False
    if user.birth_date is None:
        return False
    return True