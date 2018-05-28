
import pytest
import itertools
from bl import pwd


def test_randpwd_length():
    "the password must be the given length, default = pwd.DEFAULT_LENGTH"
    assert len(pwd.randpwd()) == pwd.DEFAULT_LENGTH
    for n in range(3, 100):
        password = pwd.randpwd(length=n)
        assert len(password) == n


def test_randpwd_default_charsets():
    charsets = pwd.DEFAULT_CHARSETS
    charset = list(itertools.chain(*charsets))
    for password in [pwd.randpwd() for i in range(100)]:
        for c in password:
            assert c in charset


def test_randpwd_custom_charsets():
    charsets = [pwd.UPPERCASE, pwd.LOWERCASE, pwd.SYMBOLS]
    charset = list(itertools.chain(*charsets))
    for password in [pwd.randpwd(charsets=charsets) for i in range(100)]:
        for c in password:
            assert c in charset


def test_randpwd_require_all_charsets():
    charsets = pwd.DEFAULT_CHARSETS
    for i in range(100):
        password = pwd.randpwd(length=len(charsets), require_all_charsets=True)
        found_charsets = []
        for c in password:
            for charset in charsets:
                if c in charset:
                    found_charsets.append(charset)
                    continue
        assert len(found_charsets) == len(charsets)
    with pytest.raises(AssertionError):
        password = pwd.randpwd(length=len(charsets) - 1, require_all_charsets=True)
