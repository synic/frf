#!/usr/bin/env python

import argparse
import importlib
import sys

import tabulate

try:
    import pyfiglet
except ImportError:
    pyfiglet = None

from frf import conf
from frf.utils.cli import colors

globalparser = argparse.ArgumentParser(
    description='Run management commmands.', add_help=False)
globalparser.add_argument(
    'command', help='The command to run.', nargs='?')


class CommandArgumentParser(argparse.ArgumentParser):
    def __init__(self, command, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command = command

    def format_usage(self):
        usage = super().format_usage()
        words = usage.split()
        words.insert(2, self.command)
        return ' '.join(words)

    def error(self, message):
        sys.stdout.writelines([
            self.format_usage(),
            '\n\n{}'.format(message),
            ])
        sys.exit(-1)


def find_commands():
    """Load command modules.

    Loads the default command modules, plus the modules from the
    `COMMAND_MODULES` setting.
    """
    module_names = [
        'frf.commands.runserver',
        'frf.commands.shell',
        'frf.commands.test',
        'frf.commands.syncdb',
        'frf.commands.startapp',
        ]

    module_names += conf.get('COMMAND_MODULES', [])

    commands = {}

    for module_name in module_names:
        module = importlib.import_module(module_name)
        cls = getattr(module, 'Command', None)
        if not cls:
            sys.stderr.write(
                'Could not get management command'
                ' from class: {}.Command\n'.format(module_name))
            sys.exit(-1)
        command_name = module_name[module_name.rfind('.') + 1:]
        commands[command_name] = cls

    return commands


def main():
    """The main command loader.

    Args:
        module_name (str): The main module name (where `app.init()` lives).
    """
    if pyfiglet:
        figlet = pyfiglet.Figlet(font='slant')
        text = figlet.renderText(conf.get('PROJECT_NAME'))
    else:
        text = conf.get('PROJECT_NAME', 'frf') + '\n'

    col = colors.ColorText()
    sys.stdout.writelines([
        col.lightmagenta(text).value(), '~' * 70, '\n'])

    argv = sys.argv[:]
    args, _ = globalparser.parse_known_args()
    commands = find_commands()

    if args.command:
        if args.command not in commands:
            sys.stderr.writelines([
                'Command not found: {}\n\n'.format(args.command),
                '\n'])
            sys.exit(-1)

        argv = argv[2:]

        # create a new parser
        parser = CommandArgumentParser(
            args.command, description='Run management commands.')
        command = commands[args.command]()
        command.add_arguments(parser)

        if getattr(command, 'parse_arguments', True):
            args = parser.parse_args(argv)

        command.handle(args)
    else:
        sys.stdout.writelines([
            'usage: manage.py [command] [options]...\n\n',
            'The following commands are available:\n\n',
            ])
        table = []

        keys = list(commands.keys())
        keys.sort()

        for command in keys:
            cls = commands.get(command)
            table.append((
                col.reset(' ').green(command).reset('').value(),
                col.reset('- ').reset(getattr(
                    cls, 'description', 'no description provided')).value()))

        sys.stdout.writelines([
            tabulate.tabulate(table, tablefmt='plain'), '\n'])
