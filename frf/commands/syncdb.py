# Copyright 2016 by Teem, and other contributors,
# as noted in the individual source code files.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By contributing to this project, you agree to also license your source
# code under the terms of the Apache License, Version 2.0, as described
# above.

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

        if not models:
            self.error('No models were found.  Have you added your module '
                       'to "INSTALLED_MODULES"?')
        else:
            for model in models:
                if not getattr(model, '__abstract__', False):
                    self.info('Creating table {}...'.format(
                        model.__tablename__), end='')  # noqa
                    model.metadata.create_all(db.engine)
                    print(' Done.')
