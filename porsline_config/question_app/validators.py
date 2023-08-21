import re
from datetime import datetime

import jdatetime


def is_georgian_date(date):
    try:
        return bool(datetime.strptime(date, "%Y/%m/%d"))
    except ValueError:
        return False


def validate_mobile_number(number):
    """
    Validates an Iran mobile number in the format 09XXXXXXXXX.
    Returns True if the number is valid, False otherwise.
    """
    pattern = r"^09\d{9}$"
    return bool(re.match(pattern, number))


def validate_city_phone_number(number):
    """
        Validates an Iran city phone number in the format 0XX-XXXXXXXX.
        Returns True if the number is valid, False otherwise.
        """
    pattern = r'^(0[1-9][1-9]\d{8})$'
    return bool(re.match(pattern, number))


def is_persian(string):
    pattern = r'^[آ-ی]+$'
    return bool(re.match(pattern, string))


def is_english(string):
    pattern = r'^[a-zA-Z]+$'
    return bool(re.match(pattern, string))


def is_jalali_date(date):
    try:
        jdatetime.datetime.strptime(date, '%Y/%m/%d')
        return True
    except ValueError:
        return False


def is_numeric(string):
    pattern = '^[0-9]+$'
    return bool(re.match(pattern, string))


def validate_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))


def option_in_html_tag_validator(options_list: list, option_text):
    print(options_list)
    for option in options_list:
        no_tag = re.sub(r'<[^>]+>', '', option)
        if no_tag == option_text:
            return True
    return False
