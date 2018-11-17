
b2 = "01"
b8 = "01234567"
b10 = "0123456789"
b16 = "0123456789abcdef"
b36 = "0123456789abcdefghijklmnopqrstuvwxyz"
b62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
b64 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"


def int_to_base(n, base):
    assert n > 0, "the integer must be greater than 0"
    m = []
    b = len(base)
    while n > 0:
        m.append(base[n % b])
        n = n // b
    return ''.join(reversed(m))


def base_to_int(s, base):
    assert set(s) <= set(base), "all characters must be in the base set"
    b = len(base)
    n = len(s)
    i = 0
    for c in s:
        n -= 1
        i += base.index(c) * (b ** n)
    return i


def convert(s, base1, base2):
    return int_to_base(base_to_int(s, base1), base2)
