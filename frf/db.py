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
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from frf.utils.db import DatabaseError, _QueryProperty
from frf.utils.json import serialize, deserialize

engine = None
_session_maker = None
session = None


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
