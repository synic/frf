import os

from frf.commands.base import BaseCommand
from frf import conf


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
