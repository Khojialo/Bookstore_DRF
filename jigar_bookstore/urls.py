from django.urls import path, include
from rest_framework.routers import DefaultRouter
from jigar_bookstore.views import (
    CategoryViewSet,
    AuthorViewSet,
    BookViewSet,
    ReviewViewSet,
    OrderViewSet,
    PaymentViewSet,
)

router = DefaultRouter()

# 🔹 Asosiy router ro‘yxatlari
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'books', BookViewSet, basename='book')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]
