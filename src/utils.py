def pretty_time_delta(seconds: int | float) -> str:
    days = int(seconds / (60 * 60 * 24))
    hours = int((seconds - days * 60 * 60 * 24) / (60 * 60))
    minutes = int((seconds - days * 60 * 60 * 24 - hours * 60 * 60) / 60)
    seconds_ = int(seconds - days * 60 * 60 * 24 - hours * 60 * 60 - minutes * 60)

    return f'{days}days, {hours}hours, {minutes}minutes, {seconds_}seconds'


def pretty_file_size(file_size: int | float, base: int = 1024):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB', 'BB', 'NB']
    level = 0

    def next_level(size):
        nonlocal level
        if size < base:
            return size
        else:
            level += 1
            return next_level(round(size / base, 2))

    return f'{next_level(file_size)} {units[level]}'
