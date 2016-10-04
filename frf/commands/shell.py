import code

try:
    import IPython
except:
    IPython = None

from frf.commands.base import BaseCommand


class Command(BaseCommand):
    description = 'start an interactive shell'

    def handle(self, *args):
        if IPython:
            IPython.embed()
        else:
            vars = globals().copy()
            vars.update(locals())
            shell = code.InteractiveConsole(vars)
            shell.interact()
