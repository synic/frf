import contextlib
import logging

from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base

from frf.utils.db import BaseQuery
from frf.utils.json import serialize, deserialize

logger = logging.getLogger(__name__)

_DATABASE_REGISTRY = []


class BaseModel(object):
    pass


class DatabaseNotConnectedError(Exception):
    """Raise when trying to access a database that isn't connected."""
    pass


class DatabaseProtectionError(Exception):
    """Raise when calling ``drop_all`` in a non-dev setting."""
    pass


class Database(object):
    """SQLAlchemy database connection wrapper.

    Wraps the SQLAlchemy session/engine for easy management.
    """

    def __init__(self, connection_uri, *args, **kwargs):
        """Create the connection (but do not connect).

        Does not actually connect to the database, use the
        :func:`Database.initialize` to initialize and connect to the database.


        Args:
            connection_uri (str): The connection URI, in the format
                ``postgresql://postgres:@localhost:5432/dbname``.
        """
        self.sessionmaker = orm.sessionmaker(query_cls=BaseQuery)
        self.session = orm.scoped_session(self.sessionmaker)
        self._engine = None
        self.metadatas = []
        self.connection_uri = connection_uri
        self.connected = False
        self.engine_args = args
        self.engine_kwargs = kwargs

        _DATABASE_REGISTRY.append(self)

    @property
    def engine(self):
        if not self.connected:
            raise DatabaseNotConnectedError(
                'Database has not been connected.')

        return self._engine

    def create_all(self):
        """Execute table creation for all tables managed by this warpper."""

        for metadata in self.metadatas:
            metadata.create_all(self.engine)

    def drop_all(self, sure=False):
        """Drop all tables managed by this wrapper."""

        if not sure:
            raise DatabaseProtectionError(
                'Must pass `sure=True` to run this function.')

        self.session.close_all()
        for metadata in self.metadatas:
            metadata.drop_all(self.engine)

    def truncate_all(self, sure=False):
        """Truncate all tables managed by this wrapper."""

        if not sure:
            raise DatabaseProtectionError(
                'Must pass `sure=True` to run this function.')

        self.session.close_all()

        with contextlib.closing(self.engine.connect()) as con:
            for metadata in self.metadatas:
                trans = con.begin()
                for table in reversed(metadata.sorted_tables):
                    con.execute(table.delete())
                trans.commit()

    def create_base_model(self, name, *args, **kwargs):
        """Create a base model to inherit from that uses this db instance.

        Args:
            name (str): The name of the model.

        All other arguments will be passed to ``declarative_base``.
        """
        if 'cls' not in kwargs:
            kwargs['cls'] = BaseModel

        base_model = declarative_base(name=name, *args, **kwargs)

        self.metadatas.append(base_model.metadata)
        return base_model

    def connect(self, raise_exception=True):
        """Connect to the database.

        Args:
            raise_exception (bool):  If there is an error connecting to the
                database, that exception will be raised if this is ``True``.
                Set to ``False`` if you want to ignore any errors.
        """
        try:
            if 'postgres' in self.connection_uri:
                self._engine = create_engine(
                    self.connection_uri,
                    json_serializer=serialize,
                    json_deserializer=deserialize,
                    *self.engine_args,
                    **self.engine_kwargs)
            else:
                self._engine = create_engine(
                    self.connection_uri,
                    *self.engine_args,
                    **self.engine_kwargs)

            self.session.configure(bind=self._engine)
            self.connected = True
        except:
            if raise_exception:
                raise

            logger.exception(
                'Error connecting to the database at URI "{}".'.format(
                    self.connection_uri))

    def create_or_update(
            self,
            model,
            defaults=None,
            add_to_session=True,
            use_filter_by=True,
            **kwargs):
        """Create or update a row.

        Args:
            model (BaseModel): The model
            defaults (dict): If the row does not exist, and it is created, use
                these default values for the newly created row.
            add_to_session (bool): Add the new object to the SQLAlchemy
                session?
            use_filter_by (bool): Use SQLAlchemy's ``filter_by`` function.  Set
                to ``False`` if you need to make more complex queries with the
                ``filter`` function instead.
            **kwargs (dict): Look up values.
        """
        if not defaults:
            defaults = {}

        created = False

        query = self.session.query(model)

        if use_filter_by:
            obj = query.filter_by(**kwargs).first()
        else:
            obj = query.filter(**kwargs).first()

        if not obj:
            created = True
            kwargs.update(defaults)
            obj = model(**kwargs)
            if add_to_session:
                self.session.add(obj)

        return obj, created


def shutdown():
    """Shut down and cleanup all registered databases."""

    for database in _DATABASE_REGISTRY:
        database.session.rollback()
        database.session.close_all()
        database.session.remove()
