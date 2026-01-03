from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Faqat admin yozishi mumkin, boshqalar faqat o‘qiy oladi."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff


class IsSellerOrReadOnly(permissions.BasePermission):
    """Kitoblarni faqat sotuvchi (yoki admin) qo‘shishi/tahrirlashi mumkin."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (request.user.is_seller or request.user.is_staff)


class IsOwnerOrAdmin(permissions.BasePermission):
    """Foydalanuvchi faqat o‘z obyektlariga kirishi mumkin (yoki admin)."""
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user
