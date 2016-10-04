import importlib
import inspect


def import_class(cl):
    """Import a class from a string."""
    if '.' in cl:
        d = cl.rfind('.')
        classname = cl[d+1:len(cl)]
        cls = cl[0:d]
    else:
        return importlib.import_module(cl)
    m = __import__(cls, globals(), locals(), [classname])
    attr = getattr(m, classname)

    if not inspect.isclass(attr):
        raise ImportError('{} does not refer to a class.'.format(cl))

    return attr

