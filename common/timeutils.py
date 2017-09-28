def secsToTime(secs: int) -> str:
    """
    Conversion of seconds into string format mm:ss
    :param secs:
    """
    minutes, seconds = divmod(secs, 60)
    return str(minutes) + ':' + str(seconds).zfill(2)
