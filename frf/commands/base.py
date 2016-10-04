import sys
import functools

from frf.utils.cli import colors

HANDLE_MAP = {
    'RED': 'stderr',
}


class BaseCommand(object):
    description = 'Description not provided'

    def add_arguments(self, parser):
        pass

    def _output(self, message, color='RESET'):
        handle_name = HANDLE_MAP.get(color, 'stdout')
        handle = getattr(sys, handle_name)
        col = colors.ColorText()
        handle.write(col.append_text(message, color=color).value() + '\n')
        handle.flush()

    greet = functools.partialmethod(_output, color='LIGHTGREEN_EX')
    error = functools.partialmethod(_output, color='RED')
    info = functools.partialmethod(_output, color='RESET')
    warning = functools.partialmethod(_output, color='YELLOW')
