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

import os
import jinja2
import frf

from frf.commands.base import BaseCommand
from frf import conf


basedir = os.path.abspath(os.path.dirname(frf.__file__))
skeldir = os.path.join(basedir, 'skel', 'modules')


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


def copy_skel(template_name, path, **kwargs):
    with open(os.path.join(skeldir, template_name)) as h:
        t = jinja2.Template(h.read())

    with open(path, 'w') as out:
        out.write(t.render(**kwargs))


class Command(BaseCommand):
    description = 'add a new module to your project'

    def add_arguments(self, parser):
        parser.add_argument('name', help='The module name.')

    def handle(self, args):
        self.greet('Creating module "{}" in "{}"... '.format(
            args.name, conf.pathof(os.path.dirname(args.name))), end='')

        output_dir = conf.pathof(args.name)

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        touch(os.path.join(output_dir, '__init__.py'))

        for skel_file in ('models_py', 'routes_py', 'serializers_py',
                          'tests_py', 'viewsets_py'):
            copy_skel(
                skel_file,
                os.path.join(output_dir, skel_file.replace('_py', '.py')),
                project_name=conf.PROJECT_NAME, module_name=args.name)

        print('Done!')
