


def load_object(path):
    if '.' not in path:
        return None
    modulename, name = path.rsplit('.', 1)
    try:
        module = __import__(modulename, {}, {}, [''])
    except ImportError as e:
        return None
    return getattr(module, name, None)



