from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Avg, Sum, F
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from django.core.validators import RegexValidator,MaxValueValidator,MinValueValidator



# ==========================
# 🔹 Base Model
# ==========================
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ==========================
# 🔹 Custom User Model
# ==========================
class User(AbstractUser, BaseModel):
    email = models.EmailField(unique=True, verbose_name="Email manzili")
    phone_number = models.CharField(max_length=15, blank=True, verbose_name="Telefon raqami")
    is_seller = models.BooleanField(default=False, verbose_name="Sotuvchimi?")

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"


# ==========================
# 🔹 Category
# ==========================
class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="Kategoriya nomi")
    slug = models.SlugField(unique=True, blank=True, verbose_name="Slug (URL)")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"


# ==========================
# 🔹 Author
# ==========================
class Author(BaseModel):
    full_name = models.CharField(max_length=150, verbose_name="To‘liq ism")
    biography = models.TextField(blank=True, verbose_name="Biografiya")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Tug‘ilgan sana")

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Muallif"
        verbose_name_plural = "Mualliflar"


# ==========================
# 🔹 Book
# ==========================
class Book(BaseModel):
    title = models.CharField(max_length=200, verbose_name="Kitob nomi")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books", verbose_name="Muallif")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Kategoriya")
    description = models.TextField(verbose_name="Tavsif")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Narx (so‘mda)")
    stock = models.PositiveIntegerField(default=0, verbose_name="Ombordagi soni")
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, verbose_name="Muqova rasmi")
    published_date = models.DateField(null=True, blank=True, verbose_name="Nashr sanasi")
    isbn = models.CharField(
        max_length=13, unique=True,
        validators=[RegexValidator(r'^\d{13}$', 'ISBN 13 xonali raqam bo‘lishi kerak')]
    )

    def __str__(self):
        return self.title

    def get_average_rating(self):
        """Baholarning o‘rtacha qiymatini hisoblaydi (optimallashtirilgan)"""
        avg = self.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(avg or 0, 1)

    class Meta:
        verbose_name = "Kitob"
        verbose_name_plural = "Kitoblar"


# ==========================
# 🔹 Review
# ==========================
class Review(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews", verbose_name="Kitob")
    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, verbose_name="Izoh")
    likes = models.ManyToManyField(User, related_name="review_likes", blank=True, verbose_name="Layklar")
    dislikes = models.ManyToManyField(User, related_name="review_dislikes", blank=True, verbose_name="Dislayklar")



    class Meta:
        unique_together = ('user', 'book')
        verbose_name = "Sharh"
        verbose_name_plural = "Sharhlar"

    def __str__(self):
        return f"{self.user.email} → {self.book.title}"


# ==========================
# 🔹 Order
# ==========================
class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", verbose_name="Buyurtmachi")
    is_paid = models.BooleanField(default=False, verbose_name="To‘langanmi?")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Umumiy summa")
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Kutilmoqda'),
            ('paid', 'To‘landi'),
            ('cancelled', 'Bekor qilindi'),
        ],
        default='pending',
        verbose_name="Holati"
    )

    def __str__(self):
        return f"Buyurtma #{self.id} - {self.user.email}"

    def calculate_total(self):
        """Buyurtma umumiy summasini hisoblaydi"""
        total = self.items.aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0
        self.total_amount = total
        self.save(update_fields=['total_amount'])

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"


# ==========================
# 🔹 Order Item
# ==========================
class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Buyurtma")
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, verbose_name="Kitob")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Miqdor")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Narx (so‘mda)")

    def __str__(self):
        return f"{self.book.title if self.book else 'Kitob o‘chirildi'} x {self.quantity}"

    def get_total_price(self):
        """Umumiy narxni hisoblaydi"""
        return self.price * self.quantity

    class Meta:
        verbose_name = "Buyurtma mahsuloti"
        verbose_name_plural = "Buyurtma mahsulotlari"


# ==========================
# 🔹 Payment
# ==========================
class Payment(BaseModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment", verbose_name="Buyurtma")
    payment_method = models.CharField(max_length=50, verbose_name="To‘lov usuli")
    transaction_id = models.CharField(max_length=100, unique=True, verbose_name="Tranzaksiya ID")
    paid_at = models.DateTimeField(auto_now_add=True, verbose_name="To‘langan vaqt")
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Muvaffaqiyatli'),
            ('failed', 'Muvaffaqiyatsiz'),
            ('pending', 'Kutilmoqda'),
        ],
        default='pending',
        verbose_name="Holati"
    )

    def __str__(self):
        return f"To‘lov {self.transaction_id}"

    class Meta:
        verbose_name = "To‘lov"
        verbose_name_plural = "To‘lovlar"


# ==========================
# 🔹 SIGNALS
# ==========================

@receiver(post_save, sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    """Har safar buyurtma elementi o‘zgarsa — umumiy summani qayta hisoblaydi"""
    instance.order.calculate_total()


@receiver(post_save, sender=Payment)
def update_order_status_on_payment(sender, instance, **kwargs):
    """To‘lov muvaffaqiyatli bo‘lsa — buyurtma holatini 'paid' ga o‘zgartiradi"""
    if instance.status == 'success':
        instance.order.status = 'paid'
        instance.order.is_paid = True
        instance.order.save(update_fields=['status', 'is_paid'])





# book= Book.objects.first()
# book.reviews.all()
#
# review = Review.objects.first()
# review.book