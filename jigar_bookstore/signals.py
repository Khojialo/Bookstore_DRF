"""
📘 Bookstore Email Notifications
--------------------------------
Ushbu modulda yangi kitob yaratilganda (Book modeli uchun `post_save` signali)
barcha seller va admin foydalanuvchilarga xabarnoma (email) yuboriladi.

Muallif: Jigar Bookstore Team
Sana: 2025-10-30
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Book, User


@receiver(post_save, sender=Book)
def send_new_book_notification(sender, instance, created, **kwargs):
    """
    📩 Yangi kitob qo‘shilganda email yuboruvchi signal.

    Ushbu funksiya `Book` modeli uchun `post_save` signaliga ulanadi.
    Agar yangi kitob yaratilgan bo‘lsa (`created=True`), tizimdagi barcha
    `is_seller=True` bo‘lgan foydalanuvchilar hamda `is_staff=True` (adminlar)
    uchun email orqali yangi kitob haqida xabarnoma yuboradi.
    """
    if not created:
        return

    subject = "📚 Yangi kitob qo‘shildi!"
    message = (
        f"Assalomu alaykum!\n\n"
        f"Yangi kitob do‘konimizga qo‘shildi:\n"
        f"📖 Nomi: {instance.title}\n"
        f"✍️ Muallif: {getattr(instance.author, 'full_name', 'Noma’lum')}\n"
        f"💰 Narx: {instance.price} so‘m\n\n"
        f"Bookstore saytida ushbu kitobni hoziroq ko‘ring!"
    )

    # 🔹 Email yuboriladigan foydalanuvchilarni aniqlash (sellerlar va adminlar)
    seller_emails = list(
        User.objects.filter(is_seller=True).values_list("email", flat=True)
    )
    admin_emails = list(
        User.objects.filter(is_staff=True).values_list("email", flat=True)
    )

    recipients = list(set(filter(None, seller_emails + admin_emails)))

    if not recipients:
        return

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        print(f"✅ {len(recipients)} ta foydalanuvchiga email yuborildi.")
    except Exception as e:
        print(f"❌ Email yuborishda xatolik: {e}")




# from django.core.mail import send_mail
# from django.conf import settings
#
# result = send_mail(
#     subject="📬 Jigar Bookstore",
#     message="Assalomu alaykum! Bu xabar Sizga jigar bookstoreda keldi.Siz buyurtma qilgan kiotb keldi",
#     from_email=settings.DEFAULT_FROM_EMAIL,
#     recipient_list=["khojiwolverein@gmail.com"],
#     fail_silently=False,
# )
#
# print("Natija:", result)
