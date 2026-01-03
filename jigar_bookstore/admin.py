from django.contrib import admin
from .models import User, Category, Author, Book, Review, Order, OrderItem, Payment


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_seller', 'is_active')
    list_filter = ('is_staff', 'is_seller', 'is_active')
    search_fields = ('username', 'email')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'birth_date')
    search_fields = ('full_name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'price', 'isbn', 'stock')
    list_filter = ('category', 'author')
    search_fields = ('title', 'isbn')
    ordering = ('title',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('comment',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'is_paid', 'total_amount', 'created_at')
    list_filter = ('status', 'is_paid')
    search_fields = ('user__username',)
    ordering = ('-created_at',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'book', 'quantity', 'price')
    search_fields = ('book__title',)
    list_filter = ('order',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'get_amount', 'payment_method', 'status', 'paid_at')
    list_filter = ('status', 'payment_method')
    ordering = ('-paid_at',)

    def get_amount(self, obj):
        """Buyurtmaning umumiy summasini ko‘rsatadi"""
        return obj.order.total_amount
    get_amount.short_description = "To‘lov summasi"
