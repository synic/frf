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
