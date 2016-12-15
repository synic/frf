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

    def _output(self, message, color='RESET', end='\n'):
        handle_name = HANDLE_MAP.get(color, 'stdout')
        handle = getattr(sys, handle_name)
        col = colors.ColorText()
        handle.write(col.append_text(message, color=color).value() + end)
        handle.flush()

    greet = functools.partialmethod(_output, color='LIGHTGREEN_EX')
    error = functools.partialmethod(_output, color='RED')
    info = functools.partialmethod(_output, color='RESET')
    warning = functools.partialmethod(_output, color='YELLOW')
