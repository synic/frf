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

from frf import app

from . import db  # noqa, initialize the database

settingsfile = 'frf.tests.fakeproject.settings'
basedir = os.path.abspath(
    os.path.join(os.path.dirname(__file__)))

app.init('fakeproject', settingsfile, basedir,
         main_app='frf.tests.fakeproject')
