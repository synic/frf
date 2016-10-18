import falcon
import traceback
import logging
import json

from gettext import gettext as _

from falcon.errors import (  # noqa
    HTTPError, HTTPForbidden, HTTPNotAcceptable, HTTPNotFound, HTTPConflict,
    HTTPLengthRequired, HTTPPreconditionFailed, HTTPRequestEntityTooLarge,
    HTTPUnsupportedMediaType, HTTPRangeNotSatisfiable, HTTPUnprocessableEntity,
    HTTPTooManyRequests, HTTPUnavailableForLegalReasons,
    HTTPInternalServerError, HTTPBadGateway, HTTPServiceUnavailable,
    HTTPInvalidHeader, HTTPMissingHeader, HTTPInvalidParam, HTTPMissingParam,
    HTTPUnauthorized,
    )

from frf import conf


logger = logging.getLogger(__name__)


class ValidationError(HTTPError):
    def __init__(self, message):
        super().__init__(
            status=falcon.HTTP_422,
            title=_('Validation Error'),
            description=message)


class InvalidFieldException(Exception):
    """Exception to raise when a serializer contains an invalid field.

    For example: a field that requires a
    :class:`frf.serializers.ModelSerializer` that is on a
    :class:`frf.serializers.Serializer`
    """
    pass


def error_serializer(req, resp, exception):
    body = exception.to_dict()
    if conf.get('DEBUG', False):
        body['traceback'] = traceback.format_exc()

    headers = getattr(exception, 'headers')
    if headers:
        resp.set_headers(headers)

    resp.body = json.dumps(body)
