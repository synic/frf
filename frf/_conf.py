import sys
import os
import importlib
import logging

logger = logging.getLogger(__name__)


class Conf(dict):
    """FRF configuration manager.

    Imports/executes the python module referenced by ``settings_file`` and then
    puts all the toplevel variables into a dictionary like object.

    Settings are set and retrieved using either dictionary syntax, or property
    syntax.  If you are retrieving a setting using property syntax, and the
    setting does not exist, None will be returned.

    If you had a settings file like this:

    .. code-block:: python
       :caption: yourproject/settings.py

        DEBUG = False

        SQLALCHEMY_CONNECTION_URI = 'sqlite://'

    Then you could use the configuration manager like so:

    >>> from yourproject import conf
    >>> conf.STUFF  # will return None because the setting doesn't exist
    >>> conf.DEBUG
    False
    >>> conf.get('SOME_SETTING')
    >>> conf.SOME_SETTING = True
    >>> conf.get('SOME_SETTING')
    True
    >>> conf.get('OTHER_SETTING')
    >>> conf['OTHER_SETTING'] = 1
    >>> conf.OTHER_SETTING
    1
    >>>
    """
    def __init__(self, settings_file=None, basedir='.'):
        self.basedir = basedir
        if settings_file:
            self.init(settings_file, basedir)

    def init(self, settings_file, basedir='.'):
        self.basedir = basedir
        self.clear()

        try:
            conf_module = importlib.import_module(settings_file)
        except ImportError:
            logger.exception(['Error importing settings module {}'.format(
                settings_file)])
            sys.exit(-1)

        for key, value in conf_module.__dict__.items():
            if not key.startswith('_'):
                self[key] = value

        self['BASE_DIR'] = basedir

    def __getattr__(self, key):
        if key in self:
            return self[key]

    def __setattr__(self, key, value):
        self[key] = value
        super().__setattr__(key, value)

    def pathof(self, *path):
        return os.path.abspath(os.path.join(self.basedir, *path))
