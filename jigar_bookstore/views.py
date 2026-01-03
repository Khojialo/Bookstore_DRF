from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Category, Author, Book, Review, Order, OrderItem, Payment
from .serializers import (
    UserSerializer, CategorySerializer, AuthorSerializer,
    BookSerializer, ReviewSerializer, OrderSerializer,
    OrderItemSerializer, PaymentSerializer
)
from django.core.mail import send_mail
from django.conf import settings
from .permissions import IsAdminOrReadOnly, IsSellerOrReadOnly, IsOwnerOrAdmin
from django.contrib.auth import get_user_model


User = get_user_model()

# =======================
# 🔹 USER
# =======================
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email']
    ordering_fields = ['username', 'email']


# =======================
# 🔹 CATEGORY
# =======================
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']


# =======================
# 🔹 AUTHOR
# =======================
class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'biography']
    ordering_fields = ['full_name']


# =======================
# 🔹 BOOK
# =======================
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().select_related('author', 'category')
    serializer_class = BookSerializer
    permission_classes = [IsSellerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'author']
    search_fields = ['title', 'description', 'isbn']
    ordering_fields = ['price', 'title', 'id']

    def perform_create(self, serializer):
        """
        Kitob yaratishda avtomatik email yuborish.
        Seller yoki admin foydalanuvchilarga xabar yuboradi.
        """
        book = serializer.save()  # 1️⃣ Kitobni saqlaymiz

        # 2️⃣ Email yuboriladigan foydalanuvchilar
        recipients = list(
            User.objects.filter(is_seller=True).values_list('email', flat=True)
        )
        admin_emails = list(
            User.objects.filter(is_staff=True).values_list('email', flat=True)
        )
        recipients = list(set(filter(None, recipients + admin_emails)))

        # 3️⃣ Agar kamida 1ta email bo‘lsa — yuboramiz
        if recipients:
            subject = "📚 Yangi kitob qo‘shildi!"
            message = (
                f"Assalomu alaykum!\n\n"
                f"Yangi kitob qo‘shildi:\n"
                f"📖 Nomi: {book.title}\n"
                f"✍️ Muallif: {book.author.full_name}\n"
                f"💰 Narx: {book.price} so‘m\n\n"
                f"Siz Bookstore saytida uni ko‘rishingiz mumkin."
            )

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipients,
                fail_silently=False,
            )


# =======================
# 🔹 REVIEW
# =======================
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['book', 'rating']
    search_fields = ['comment']
    ordering_fields = ['created_at', 'rating']

    def get_queryset(self):
        user = self.request.user
        qs = Review.objects.select_related('book', 'user')
        if user.is_authenticated and not user.is_staff:
            return qs.filter(user=user)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# =======================
# 🔹 ORDER
# =======================
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'is_paid']
    ordering_fields = ['created_at', 'total_amount']

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.prefetch_related('items', 'items__book', 'user')
        if user.is_staff or user.is_seller:
            return qs
        return qs.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# =======================
# 🔹 ORDER ITEM
# =======================
class OrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['order', 'book']
    ordering_fields = ['price', 'quantity']

    def get_queryset(self):
        user = self.request.user
        qs = OrderItem.objects.select_related('order', 'book', 'order__user')
        if user.is_staff:
            return qs
        return qs.filter(order__user=user)


# =======================
# 🔹 PAYMENT
# =======================
class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method']
    ordering_fields = ['paid_at']

    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.select_related('order', 'order__user')
        if user.is_staff:
            return qs
        return qs.filter(order__user=user)
