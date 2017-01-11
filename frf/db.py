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

"""FRF Database access.

Configuration of the database is as easy as defining the setting
``SQLALCHEMY_CONNECTION_URI`` in your settings file, for example:

.. code-block:: python
   :caption: settings.py

   SQLALCHEMY_CONNECTION_URI = 'postgresql://postgres:@localhost/dbname'

Visit the following link for more information on the connection uri format and
supported databases: http://docs.sqlalchemy.org/en/latest/core/engines.html

Once you have it configured, you can define models and interact with the
SQLALchemy session like so (assuming your project name is ``yourproject``):

.. code-block:: python
   :caption: models.py

   import uuid
   from frf import models

   class Test(models.Model):
        uuid = models.Column(
            models.GUID, primary_key=True, default=uuid.uuid4())

        __tablename__ = 'testtable'


>>> from yourproject import db
>>> from app import models
>>> t = models.Test()
>>> db.session.add(t)
>>> db.session.commit()
>>> t = models.Test.query.first()
>>> t.uuid
UUID('2d2fac55-71e9-45c6-b349-13e706efa8f4')
>>>
"""

import contextlib
import importlib
import inspect

try:
    from factory.alchemy import SQLAlchemyModelFactory
except ImportError:
    SQLAlchemyModelFactory = None

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from frf import conf, models
from frf.exceptions import DatabaseError
from frf.utils.db import _QueryProperty
from frf.utils.json import deserialize, serialize


engine = None
_session_maker = None
session = None


def get_engine():
    """Return the current database engine."""
    return engine


def init(connection_uri, echo=False, use_greenlet_scope=False):
    """Initialize the session.

    Args:
        connection_uri (str): The connection uri, such as
            "postgrseql://user:password@localhost/dbname"
        echo (bool): Echo SQL statements to stdout.  Useful for debugging.
        use_greenlet_scope (bool): Set to `True` if you are using
            greenlets so that the session gets scoped to the correct
            identity function
    """
    global engine, _session_maker, session

    from frf.models import Model

    if use_greenlet_scope:
        # attempt to use `greenlet.get_current` as the sqlalchemy session
        # scope
        try:
            from greenlet import get_current as get_ident
        except ImportError:
            raise DatabaseError(
                'You have specified `use_greenlet_scope` in your database '
                'configuration, but greenlet could not be imported.')
    else:
        # use local thread for sqlalchemy session scope
        try:
            from thread import get_ident
        except ImportError:
            try:
                from _thread import get_ident
            except ImportError:
                # no `get_ident` could be found, just use `None`.  This
                # will create the default thread local session.
                get_ident = None

    if 'postgres' in connection_uri:
        engine = create_engine(
            connection_uri,
            echo=echo,
            json_serializer=serialize,
            json_deserializer=deserialize)
    else:
        engine = create_engine(
            connection_uri,
            echo=echo)
    _session_maker = sessionmaker(bind=engine)
    session = scoped_session(
        _session_maker, scopefunc=get_ident)

    Model.query = _QueryProperty(session)


def create_all():
    """Create all tables in the database.

    Tables that already exist in the database will not be changed.
    """
    if not engine or not session:
        raise DatabaseError('Database is not yet initialized')

    # make sure all models are imported
    for app_name in conf.get('INSTALLED_APPS', []):
        try:
            importlib.import_module('{}.models'.format(app_name))
        except ImportError:
            pass

        # fix all factories
        if SQLAlchemyModelFactory:
            try:
                module = importlib.import_module('{}.tests.factories'.format(
                    app_name))
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if inspect.isclass(attr) and issubclass(
                            attr, SQLAlchemyModelFactory):
                        attr._meta.sqlalchemy_session = session

            except ImportError:
                pass

    models.Model.metadata.create_all(engine)


def drop_all():
    """Drop all tables from the database.

    An error will NOT be thrown if a table does not exist in the database.
    """
    if not engine or not session:
        raise DatabaseError('Database is not yet initialized')

    session.close()

    for app_name in conf.get('INSTALLED_APPS', []):
        try:
            importlib.import_module('{}.models'.format(
                app_name))
        except ImportError:
            pass

    models.Model.metadata.drop_all(engine)


def truncate_all():
    """Truncate all tables.

    Useful for the testing databases.
    """
    if not engine or not session:
        raise DatabaseError('Database is not yet initialized')

    session.close()

    with contextlib.closing(engine.connect()) as con:
        trans = con.begin()
        for app_name in conf.get('INSTALLED_APPS', []):
            try:
                module = importlib.import_module('{}.models'.format(
                    app_name))
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if inspect.isclass(attr) and issubclass(
                            attr, models.Model):

                        # truncate the table
                        con.execute(attr.__table__.delete())

            except ImportError:
                pass

        trans.commit()
