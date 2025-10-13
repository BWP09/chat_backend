import datetime, pytz

_date_time_replace = {
    "{day}": "%d",
    "{month}": "%m",
    "{year2}": "%y",
    "{year4}": "%Y",
    "{second}": "%S",
    "{minute}": "%M",
    "{hour12}": "%I",
    "{hour24}": "%H",
    "{ampm}": "%p",

    "{d}": "%d",
    "{m}": "%m",
    "{y2}": "%y",
    "{y4}": "%Y",
    "{sec}": "%S",
    "{min}": "%M",
    "{h12}": "%I",
    "{h24}": "%H",
    "{ampm}": "%p",
}

def dt_parse(datetime_str: str) -> str:
    for k, v in _date_time_replace.items():
        datetime_str = datetime_str.replace(k, v)

    return datetime_str

def time_ago(unix_timestamp: int, timezone_str: str = "UTC") -> str:
    tz = pytz.timezone(timezone_str)
    now = datetime.datetime.now(tz)
    past = datetime.datetime.fromtimestamp(float(unix_timestamp), tz)
    diff = now - past

    if diff < datetime.timedelta(minutes = 1):
        seconds = int(diff.total_seconds())
        return f"{seconds} second{"s" if seconds > 1 else ""} ago"

    elif diff < datetime.timedelta(hours = 1):
        minutes = int(diff.total_seconds() // 60)
        return f"{minutes} minute{"s" if minutes > 1 else ""} ago"

    elif diff < datetime.timedelta(days = 1):
        hours = int(diff.total_seconds() // 3600)
        return f"{hours} hour{"s" if hours > 1 else ""} ago"

    elif diff < datetime.timedelta(weeks = 1):
        days = diff.days
        return f"{days} day{"s" if days > 1 else ""} ago"

    elif diff < datetime.timedelta(days = 30):
        weeks = diff.days // 7
        return f"{weeks} week{"s" if weeks > 1 else ""} ago"

    elif diff < datetime.timedelta(days = 365):
        months = diff.days // 30
        return f"{months} month{"s" if months > 1 else ""} ago"

    else:
        years = diff.days // 365
        return f"{years} year{"s" if years > 1 else ""} ago"

