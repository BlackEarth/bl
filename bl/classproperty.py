class classproperty:
    """
    Decorate a method with `@classproperty` to make a class-level property. Read only.
    """

    def __init__(self, method=None):
        self.method = method

    def __get__(self, _, cls=None):
        return self.method(cls)
