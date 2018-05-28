
import itertools
from random import randrange

UPPERCASE = [chr(i) for i in range(65, 91)]  # A to Z
LOWERCASE = [chr(i) for i in range(97, 123)]  # a to z
NUMBERS = [chr(i) for i in range(48, 58)]  # 0 to 9
SYMBOLS = [chr(i) for i in range(33, 48)]  # ! to /
DEFAULT_CHARSETS = [UPPERCASE, LOWERCASE, NUMBERS]
DEFAULT_LENGTH = 8


def randpwd(length=DEFAULT_LENGTH, charsets=DEFAULT_CHARSETS, require_each=False):
    l = []
    if require_each == True:
        assert length >= len(charsets)
        # get one character from each charset
        for i in range(len(charsets)):
            charset = charsets[i]
            l.append(charset[randrange(len(charset))])
    # get the rest of the characters from the whole charset
    charset = list(itertools.chain(*charsets))
    l += [charset[randrange(len(charset))] for i in range(len(l), length)]
    # mix all the characters for additional randomness
    for i in range(len(l)):
        pos = randrange(len(l))
        l[i], l[pos] = l[pos], l[i]
    return "".join(l)


# -- TESTS --
import pytest


def test_randpwd_length():
    "the password must be the given length, default = DEFAULT_LENGTH"
    assert len(randpwd()) == DEFAULT_LENGTH
    for n in range(3, 100):
        password = randpwd(length=n)
        assert len(password) == n


def test_randpwd_default_charsets():
    charsets = DEFAULT_CHARSETS
    charset = list(itertools.chain(*charsets))
    for password in [randpwd() for i in range(100)]:
        for c in password:
            assert c in charset


def test_randpwd_custom_charsets():
    charsets = [UPPERCASE, LOWERCASE, SYMBOLS]
    charset = list(itertools.chain(*charsets))
    for password in [randpwd(charsets=charsets) for i in range(100)]:
        for c in password:
            assert c in charset


def test_randpwd_require_each():
    charsets = DEFAULT_CHARSETS
    for i in range(100):
        password = randpwd(length=len(charsets), require_each=True)
        found_charsets = []
        for c in password:
            for charset in charsets:
                if c in charset:
                    found_charsets.append(charset)
                    continue
        assert len(found_charsets) == len(charsets)
    with pytest.raises(AssertionError):
        password = randpwd(length=len(charsets) - 1, require_each=True)
