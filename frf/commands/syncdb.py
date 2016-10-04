import inspect
import importlib

from frf.commands.base import BaseCommand
from frf import models as falconmodels

from frf import conf, db


class Command(BaseCommand):
    decription = 'create any uncreated tables in the database'

    parse_arguments = False

    def handle(self, args):
        models = []
        for module_name in conf.get('INSTALLED_MODULES', []):
            module = importlib.import_module(
                '{}.models'.format(module_name))
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if inspect.isclass(attr) and issubclass(
                        attr, falconmodels.Model):
                    models.append(attr)

        for model in models:
            if not getattr(model, '__abstract__', False):
                print('Creating table {}...'.format(
                    model.__tablename__), end='')  # noqa
                model.metadata.create_all(db.engine)
                print(' Done.')
