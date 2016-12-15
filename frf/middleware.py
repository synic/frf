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

from frf import db


class SQLAlchemyMiddleware(object):
    """SQLAlchemy session manager middleware.

    If you plan on using the database in any of your sessions, you MUST include
    this middleware in your falcon instance, and it MUST appear before any
    other middleware that uses the database in any of it's handlers.

    This is because this middleware does nothing but make sure the database
    session is closed at the end of the request.

    To enable, add to your `MIDDLEWARE_CLASSES` in your settings, IE:

    ```python
    MIDDLEWARE_CLASSES = [
        'frf.middleware.SQLAlchemyMiddleware',
        'someapp.middleware.AuthenticationMiddleware',
    ]
    ```
    """
    def process_response(self, req, resp, resource):
        # close db session
        db.session.remove()
