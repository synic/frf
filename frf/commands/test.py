import pytest
import sys

from frf.commands.base import BaseCommand
from frf import conf


class Command(BaseCommand):
    description = 'run unittests'

    parse_arguments = False

    def handle(self, args):
        conf['TESTING'] = True

        sys.argv = sys.argv[1:]

        sys.exit(pytest.main())
