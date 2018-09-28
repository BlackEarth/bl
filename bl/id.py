"""
Create a variety of different random ids.

id.random_id() returns a random_id with the given parameters.

id.hex_chars is 16 characters long, so you need a much longer string for the 
same level of security, but some contexts need hex.
    + 16^8 = 4.3 billion unique ids.

id.alphanum_chars is 62 characters long, so it is plenty for uniqueness and 
non-discoverability for most circumstances. For example:
    + 62^6 = 5.68e10, which is the length of a bit.ly id (56.8 billion unique URLs).
    + 62^16 = 4.77e28, which is huge 
    + 62^32 = 2.27e57, which is overkill by a lot -- we'll never get a repeat, and we can test for it.

id.b64_chars are the 64 characters allowed in url-safe base64 encoding
    + 64^6 = 6.87e10
    + 64^16 = 7.92e28
    + 64^32 = 6.28e57

id.punct_chars has most ascii punctuation.

id.ascii_chars = id.alphanum_chars + id.punct_chars.

urlslug_chars adds to id.alphanum_chars certain punctuation that is allowed 
in urls. 72 characters. This is useful for URL shorteners.
    + 72^4 = 26.9 million unique URL slugs. 
    + So a private URL shortener can be like the following:
        - www.tld.to/YpH0
    which exactly fits the size for micro-QR codes (15 characters).
    (This is exactly the size of links from www.goo.gl )
"""

import random

lcase_chars = (
    ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    + ['k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't']
    + ['u', 'v', 'w', 'x', 'y', 'z']
)
ucase_chars = [c.upper() for c in lcase_chars]
num_chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
hex_chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
alpha_chars = lcase_chars + ucase_chars
alphanum_chars = alpha_chars + num_chars
b64_chars = alphanum_chars + ['-', '_']
id_chars = alphanum_chars  # conservative defaults work everywhere
id_first_chars = alpha_chars
punct_chars = (
    ['~', '!', '@', '#', '$', '%', '^', '&', '*', '(']
    + [')', '_', '-', '+', '=', '[', '{', ']', '}', '|']
    + [';', ':', ',', '<', '.', '>', '/', '?']
)
ascii_chars = alphanum_chars + punct_chars
urlslug_punct = ['-', '_', '.', '+', '!', '*', "'", '(', ')', ',']
urlslug_chars = alphanum_chars + urlslug_punct
slug_chars = urlslug_chars


def random_id(length=16, charset=alphanum_chars, first_charset=alpha_chars, sep='', group=0):
    """Creates a random id with the given length and charset.
    ## Parameters
    * length          the number of characters in the id
    * charset         what character set to use (a list of characters)
    * first_charset   what character set for the first character
    * sep=''          what character to insert between groups
    * group=0         how long the groups are (default 0 means no groups)
    """
    t = []

    first_chars = list(set(charset).intersection(first_charset))
    if len(first_chars) == 0:
        first_chars = charset

    t.append(first_chars[random.randrange(len(first_chars))])

    for i in range(len(t), length):
        if (group > 0) and (i % group == 0) and (i < length):
            t.append(sep)
        t.append(charset[random.randrange(len(charset))])

    return ''.join(t)
