def protected_http_method(func):
    """Decorate your controller function with
    this decorator if requested user must
    be authorized.

    """
    func.__setattr__('protected', True)

    def inner(*args, **kwargs):
        return func(args, kwargs)

    return inner
