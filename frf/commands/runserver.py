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

from frf import conf
from frf.commands.base import BaseCommand


class Command(BaseCommand):
    description = 'start a gunicorn server'

    def add_arguments(self, parser):
        parser.add_argument(
            '-b', '--bind', help='Address to bind to', default='0.0.0.0:8080')
        parser.add_argument(
            '-t', '--threads', help='Number of threads', default=1)
        parser.add_argument(
            '-w', '--workers', help='Number of workers', default=2)
        parser.add_argument(
            '-r', '--reload', action='store_const', const='reload',
            default='reload', help='Reload on code change')

        default = 30
        if conf.DEBUG:
            default = 120
        parser.add_argument(
            '-T', '--timeout', help='Worker timeout', default=default)

    def handle(self, args):
        self.greet('Oh hai, starting gunicorn...')
        app_name = os.path.basename(conf.get('BASE_DIR'))
        os.system(
            'gunicorn {} --access-logfile - --error-logfile - --bind {} '
            '--workers {} --timeout {} --threads {} {}:app.api'.format(
                '--reload' if args.reload == 'reload' else '',
                args.bind,
                args.workers,
                args.timeout,
                args.threads,
                app_name,
            ))
