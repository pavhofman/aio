import decimal


def clamp(n, minn, maxn):
    if n < minn:
        return minn
    elif n > maxn:
        return maxn
    else:
        return n


def roundToInt(timePos: float) -> int:
    return int(decimal.Decimal(timePos).quantize(decimal.Decimal(1),
                                                 rounding=decimal.ROUND_HALF_UP))
