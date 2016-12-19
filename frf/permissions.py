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
