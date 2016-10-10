import sys

from ._conf import Conf

conf = Conf()
conf.__file__ = __file__
sys.modules[__name__] = conf
