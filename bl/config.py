
import os, re
from configparser import ConfigParser, ExtendedInterpolation
from bl.dict import Dict         # needed for dot-attribute notation

LIST_PATTERN = "^\[\s*([^,]*)\s*(,\s*[^,]*)*,?\s*\]$"
DICT_ELEM = """(\s*['"].+['"]\s*:\s*[^,]+)"""
DICT_PATTERN = """^\{\s*(%s,\s*%s*)?,?\s*\}$""" % (DICT_ELEM, DICT_ELEM)

class Config(Dict):
    """class for holding application configuration in an Ini file. Sample Usage:
    >>> cf_filename = os.path.join(os.path.dirname(__file__), "config_test.ini")
    >>> cf = Config(cf_filename)
    >>> cf.Archive.path             # basic string conversion
    '/data/files'
    >>> cf.Test.debug               # boolean 
    True
    >>> cf.Test.list                # list with several types
    [1, 2, 'three', True, 4.0]
    >>> cf.Test.dict                # dict => Dict
    {'a': 1, 'b': 'two', 'c': False}
    >>> cf.Test.dict.a              # Dict uses dot-notation
    1
    """

    def __init__(self, filename, interpolation=ExtendedInterpolation(), **kwargs):
        config = ConfigParser(interpolation=interpolation, **kwargs)
        self.__dict__['__file__'] = filename
        if config.read(filename):
            self.parse_config(config)
        else:
            raise KeyError("Config file not found at %s" % filename)

    def __repr__(self):
        return "Config('%s')" % self.__file__

    def parse_config(self, config):
        for s in config.sections():
            self[s] = Dict()
            for k, v in config.items(s):
                # resolve common data types
                if v.lower() in ['true', 'false', 'yes', 'no']:     # boolean
                    self[s][k] = config.getboolean(s, k)
                elif re.match("^\-?\d+$", v):                       # integer
                    self[s][k] = int(v)
                elif re.match("^\-?\d+\.\d*$", v):                  # float
                    self[s][k] = float(v)
                elif re.match(LIST_PATTERN, v):                     # list
                    self[s][k] = eval(v)
                elif re.match(DICT_PATTERN, v):                     # dict
                    self[s][k] = Dict(**eval(v))
                else:                                               # default: string
                    self[s][k] = v.strip()

    def write(self, fn=None, sorted=True):
        """write the contents of this config to fn or its __file__.
        NOTE: All interpolations will be expanded in the written file.
        """
        config = ConfigParser(interpolation=None)
        keys = self.keys()
        if sorted==True: keys.sort()
        for key in keys:
            config[key] = {}
            ks = self[key].keys()
            if sorted==True: ks.sort()
            for k in ks:
                config[key][k] = str(self[key][k])
        with open(fn or self.__file__, 'w') as f:
            config.write(f)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
