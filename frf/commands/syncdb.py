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

import importlib
import inspect

from frf import conf, db
from frf import models as falconmodels
from frf.commands.base import BaseCommand


class Command(BaseCommand):
    decription = 'create any uncreated tables in the database'

    parse_arguments = False

    def handle(self, args):
        models = []
        for app_name in conf.get('INSTALLED_APPS', []):
            models_module = importlib.import_module(
                '{}.models'.format(app_name))
            for attr_name in dir(models_module):
                attr = getattr(models_module, attr_name)
                if inspect.isclass(attr) and issubclass(
                        attr, falconmodels.Model):
                    models.append(attr)

        if not models:
            self.error(
                'No models were found.  Have you added your app '
                'to "INSTALLED_APPS"?')
        else:
            self.info('Creating tables...', end='')
            falconmodels.Model.metadata.create_all(db.engine)
            self.info(' Done.')
