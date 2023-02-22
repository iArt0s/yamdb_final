from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Класс Permission, ограничивающий доступ к UnSAFE methods."""

    def has_permission(self, request, view):

        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and (request.user.is_admin
                     or request.user.is_staff))


class IsOnlyAdmin(permissions.BasePermission):
    """Класс Permission, доступ для админов."""

    def has_permission(self, request, view):

        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_staff)


class IsReviewAndComment(permissions.BasePermission):
    """Класс Permission, ограничивающий доступ к отзывам и комментам."""

    def has_object_permission(self, request, view, obj):

        return (
            request.method not in permissions.SAFE_METHODS
            and (request.user.is_authenticated
                 and (request.user == obj.author
                      or request.user.is_admin
                      or request.user.is_moderator
                      or request.user.is_staff))
            or request.method == ('GET')
        )
