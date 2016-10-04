import sys

from ._conf import Conf

sys.modules[__name__] = Conf()
