class Str:
    """
    Typing helper to describe type that use bytes in py2 and text in py3.
    """
    def __init__(self, obj: object = ..., /) -> None: ...

    __bool__: ...
