import re
import jdatetime


def is_georgian_date(date):
    pattern = r'^\d{1,2}/\d{1,2}/\d{4}$'

    if not re.match(pattern, date):
        return False

    day, month, year = map(int, date.split('/'))

    if year < 1000 or year > 9999:
        return False

    if month < 1 or month > 12:
        return False

    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if month == 2 and year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        month_days[1] += 1
    if day < 1 or day > month_days[month - 1]:
        return False

    return True


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
