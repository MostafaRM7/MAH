from user_app.models import Profile


def validate_user_info(user: Profile):
    errors = {}
    try:
        if user.wallet is None:
            errors.update({'wallet': 'کاربر کیف پول ندارد'})
    except:
        errors.update({'wallet': 'کاربر کیف پول ندارد'})
    if user.first_name is None or user.first_name == '':
        errors.update({'first_name': 'نام کاربر خالی است'})
    if user.last_name is None or user.last_name == '':
        errors.update({'last_name': 'نام خانوادگی کاربر خالی است'})
    if user.email is None or user.email == '':
        errors.update({'email': 'ایمیل کاربر خالی است'})
    # if user.preferred_districts.all().exists() is False:
    #     errors.update({'preferred_districts': 'مناطق پرسشگری کاربر خالی است'})
    if user.province is None:
        errors.update({'province': 'استان کاربر خالی است'})
    if user.nationality is None:
        errors.update({'nationality': 'ملیت کاربر خالی است'})
    if user.gender is None or user.gender == '':
        errors.update({'gender': 'جنسیت کاربر خالی است'})
    # if user.birth_date is None:
    #     errors.update({'birth_date': 'تاریخ تولد کاربر خالی است'})
    if user.resume is None:
        errors.update({'resume': 'رزومه کاربر خالی است'})
    if len(errors) > 0:
        return False, errors
    return True, errors
