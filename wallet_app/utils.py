from datetime import datetime


def is_valid_date(date_string):
    try:
        datetime.fromisoformat(date_string)
    except ValueError:
        return False
    return True
