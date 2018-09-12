import json


class No:
    def __bool__(self):
        return False

    def __repr__(self):
        return 'No'

    def __str__(self):
        return ''

    def __getattr__(self, key):
        return No()

    def __getitem__(self, key):
        return No()


class NoDict(dict):
    def __call__(self, **kwargs):
        return self.__class__(self, **kwargs)

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except:
            return No()

    def __setattr__(self, key, val):
        self.__setitem__(key, val)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({', '.join(['%s=%r' % (k, self[k]) for k in self.keys()])})"
        )

    def __str__(self):
        return json.dumps(self)


class SortedNoDict(NoDict):
    """Dict with keys sorted."""

    def keys(self, key=None, reverse=False):
        return sorted(super().keys(), key=key, reverse=reverse)

    def values(self, key=None, reverse=False):
        return [self[k] for k in self.keys(key=key, reverse=reverse)]
