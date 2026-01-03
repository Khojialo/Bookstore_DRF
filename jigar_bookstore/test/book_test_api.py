from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from jigar_bookstore.models import (
    User, Category, Author, Book
)
from jigar_bookstore.serializers import BookSerializer


class BookstoreAPITestCase(APITestCase):

    def setUp(self):
        """Har bir testdan oldin bazani tozalaymiz va ma'lumotlarni qayta yaratamiz"""
        # Tozalash
        Book.objects.all().delete()
        Category.objects.all().delete()
        Author.objects.all().delete()
        User.objects.all().delete()

        # 🔹 Foydalanuvchilar
        self.user = User.objects.create_user(
            username='ali',
            email='ali@example.com',
            password='ali12345@'
        )
        self.seller = User.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='seller12345@',
            is_seller=True
        )

        # 🔹 Kategoriyalar
        self.category1 = Category.objects.create(name="Fantastika")
        self.category2 = Category.objects.create(name="Tarixiy")

        # 🔹 Mualliflar
        self.author1 = Author.objects.create(full_name="Ali Akbar", biography="Fantast yozuvchi")
        self.author2 = Author.objects.create(full_name="Ortikboy Qahhor", biography="Tarixchi yozuvchi")

        # 🔹 Kitoblar
        self.book1 = Book.objects.create(
            title="Sehrli Dunyo",
            author=self.author1,
            category=self.category1,
            description="Qiziqarli hikoya",
            price=55000,
            stock=12,
            isbn="1234567890123"
        )
        self.book2 = Book.objects.create(
            title="Tarix Sirlari",
            author=self.author2,
            category=self.category2,
            description="Tarix haqida",
            price=70000,
            stock=5,
            isbn="9876543210123"
        )

        # 🔹 Login
        token_url = reverse('login')
        response = self.client.post(token_url, data={'username': 'ali', 'password': 'ali12345@'})
        if 'auth_token' in response.data:
            token = response.data['auth_token']
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        else:
            self.client.force_authenticate(user=self.user)

        self.list_url = reverse('book-list')

    # ====================================================
    # 🔹 CREATE
    # ====================================================
    def test_create_book(self):
        data = {
            "title": "Yangi Kitob",
            "author": str(self.author1.id),
            "category": str(self.category1.id),
            "description": "Zo‘r kitob",
            "price": "65000",
            "stock": 10,
            "isbn": "9999999999999"
        }
        self.client.force_authenticate(user=self.seller)
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("✅ Kitob muvaffaqiyatli yaratildi:", response.data)

    # ====================================================
    # 🔹 UPDATE (PUT)
    # ====================================================
    def test_update_book_put(self):
        url = reverse('book-detail', args=[self.book1.id])
        self.client.force_authenticate(user=self.seller)
        data = {
            "title": "Yangi Sehrli Dunyo",
            "author": str(self.author1.id),
            "category": str(self.category1.id),
            "description": "Yangilangan tavsif",
            "price": 60000,
            "stock": 15,
            "isbn": self.book1.isbn
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, "Yangi Sehrli Dunyo")
        print("✅ Kitob PUT orqali yangilandi:", response.data)

    # ====================================================
    # 🔹 UPDATE (PATCH)
    # ====================================================
    def test_update_book_patch(self):
        url = reverse('book-detail', args=[self.book1.id])
        data = {"title": "Patch Yangilandi", "price": 99999}
        self.client.force_authenticate(user=self.seller)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, "Patch Yangilandi")
        print("✅ Kitob PATCH orqali qisman yangilandi:", response.data)

    # ====================================================
    # 🔹 GET (LIST)
    # ====================================================
    def test_get_book_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)
        print("✅ Kitoblar ro‘yxati olindi:", results)

    # ====================================================
    # 🔹 GET (DETAIL)
    # ====================================================
    def test_get_book_detail(self):
        url = reverse('book-detail', args=[self.book1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.book1.title)
        print("✅ Kitob tafsiloti olindi:", response.data)

    # ====================================================
    # 🔹 DELETE
    # ====================================================
    def test_delete_book(self):
        url = reverse('book-detail', args=[self.book1.id])
        self.client.force_authenticate(user=self.seller)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        exists = Book.objects.filter(id=self.book1.id).exists()
        self.assertFalse(exists)
        print(f"✅ Kitob ID={self.book1.id} muvaffaqiyatli o‘chirildi.")

    # ====================================================
    # 🔹 ORDERING
    # ====================================================
    def test_get_order_books(self):
        response = self.client.get(self.list_url, {'ordering': 'price'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("✅ Kitoblar tartib bilan olindi:", response.data)

    # ====================================================
    # 🔹 FILTER
    # ====================================================
    def test_filter_books_by_category(self):
        response = self.client.get(self.list_url, {'category': str(self.category1.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(str(results[0]['category']), str(self.category1.id))
        print("✅ Kategoriya bo‘yicha filtr ishladi:", results)

    # ====================================================
    # 🔹 SEARCH
    # ====================================================
    def test_search_books(self):
        response = self.client.get(self.list_url, {'search': 'Sehrli'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "Sehrli Dunyo")
        print("✅ SearchFilter ishladi. Natija:", results)

    # ====================================================
    # 🔹 SERIALIZER FIELDS
    # ====================================================
    def test_serializer_fields(self):
        serializer = BookSerializer(self.book1)
        data = serializer.data
        self.assertIn('average_rating', data)
        self.assertIn('author_detail', data)
        self.assertIn('category_detail', data)
        print("✅ Serializer fieldlari to‘g‘ri chiqdi:", data.keys())
