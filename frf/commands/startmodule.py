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
