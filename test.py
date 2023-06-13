from datetime import datetime, timedelta

times = [
    datetime.now() + timedelta(minutes=6),
    datetime.now() + timedelta(minutes=7),
    datetime.now() + timedelta(minutes=8),
    datetime.now() + timedelta(minutes=9),
    datetime.now() + timedelta(minutes=10),
    datetime.now() + timedelta(minutes=11),
    datetime.now() + timedelta(minutes=12),
    datetime.now() + timedelta(minutes=13),
    datetime.now() + timedelta(minutes=14),
    datetime.now() + timedelta(minutes=15),
]

def find_time_splits(datetime_list: list):
    now = datetime.now()
    seconds_between = [(datetime_list[0] - now).total_seconds()]

    for i, dt in enumerate(datetime_list):
        if dt == datetime_list[0]:
            continue
        diff = dt - datetime_list[i-1]
        seconds_between.append(diff.seconds)

    return seconds_between

print(find_time_splits(times))