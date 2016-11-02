class BasePermission(object):
    """Base permission class.

    Other permissions can inherit from this, and need to override
    ``has_permission``.

    For example:

    .. code-block:: python
       :caption: permissions.python

       from frf import permissions

       class StaffRequiredPermission(permissions.BasePermission):
            '''Require staff permissions.'''
            def has_permission(self, req, view, **kwargs):
                user = req.context.get('user', None)
                return user it not None and user.is_staff
    """
    def has_permission(self, req, view, **kwargs):
        """Check permission.

        Args:
            req (falcon.request.Request): The request object
            resp (falcon.response.Response): The response object
            view (frf.views.View): The view object

        Returns:
            bool: return ``True`` if the user has permission for the
                operation.
        """
        return False
