from frf import conf as baseconf


class OverrideSettingsManager(object):
    """Temporarily override settings in a context manager.

    Use the ``override_settings`` alias.

    Usage example:

    .. code-block:: python

        from frf import conf
        from frf.utils.conf import override_settings

        conf['TEST'] = 1
        print(conf.TEST)   #  Should be 1

        with override_settings(TEST=2):
            print(conf.TEST)  # should be 2

        print(conf.TEST)   #  Should be 1
    """

    def __init__(self, conf=None, **kwargs):
        self.kwargs = kwargs
        self.oldsettings = dict()
        self.conf = conf if conf else baseconf

    def __enter__(self):
        self.oldsettings.clear()

        for key in self.kwargs.keys():
            self.oldsettings[key] = self.conf.get(key, None)

        for key, value in self.kwargs.items():
            self.conf[key] = value

    def __exit__(self, *exc):
        for k, v in self.oldsettings.items():
            self.conf[k] = v


override_settings = OverrideSettingsManager
