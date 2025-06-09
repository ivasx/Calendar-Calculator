import datetime
from functools import wraps

def format_date(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        if isinstance(result, datetime.datetime):
            return result.strftime('%d.%m.%Y')
        return result
    return wrapper