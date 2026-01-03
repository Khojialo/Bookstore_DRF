from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from django.urls import reverse

from jigar_bookstore.models import (
    User, Category, Author, Book, Review
)
from jigar_bookstore.serializers import ReviewSerializer


class ReviewAPITestCase(APITestCase):
    """Review API uchun to‘liq testlar"""

    def setUp(self):
        """Har bir testdan oldin bazani tozalaymiz va yangidan ma'lumot yaratamiz"""
        Review.objects.all().delete()
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
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin12345@'
        )

        # 🔹 Kategoriya & Muallif & Kitob
        self.category = Category.objects.create(name="Fantastika")
        self.author = Author.objects.create(full_name="Ali Akbar", biography="Fantast yozuvchi")
        self.book = Book.objects.create(
            title="Sehrli Dunyo",
            author=self.author,
            category=self.category,
            description="Fantastik hikoya",
            price=55000,
            stock=10,
            isbn="1234567890123"
        )

        # 🔹 Review (bir dona mavjud)
        self.review = Review.objects.create(
            user=self.user,
            book=self.book,
            rating=5,
            comment="Zo‘r kitob!"
        )

        # 🔹 Login
        token_url = reverse('login')
        response = self.client.post(token_url, data={'username': 'ali', 'password': 'ali12345@'})
        if 'auth_token' in response.data:
            token = response.data['auth_token']
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        else:
            self.client.force_authenticate(user=self.user)

        # 🔹 API Request Factory (serializer uchun kerak bo‘ladi)
        self.factory = APIRequestFactory()

        # 🔹 Base URL
        self.list_url = reverse('review-list')

    # ====================================================
    # 🔹 CREATE
    # ====================================================
    def test_create_review(self):
        """Yangi review yaratish — har xil kitob uchun"""
        # yangi kitob yaratamiz, chunki user bir kitobga faqat bitta review yozishi mumkin
        new_book = Book.objects.create(
            title="Tarix Sirlari",
            author=self.author,
            category=self.category,
            description="Tarixiy hikoya",
            price=70000,
            stock=5,
            isbn="9876543210123"
        )
        data = {
            "book": str(new_book.id),
            "rating": 4,
            "comment": "Yaxshi kitob"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("✅ Review muvaffaqiyatli yaratildi:", response.data)

    # ====================================================
    # 🔹 UPDATE (PATCH)
    # ====================================================
    def test_update_review_patch(self):
        url = reverse('review-detail', args=[self.review.id])
        data = {"rating": 3, "comment": "Tuzatildi"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 3)
        print("✅ Review PATCH orqali yangilandi:", response.data)

    # ====================================================
    # 🔹 GET (LIST)
    # ====================================================
    def test_get_review_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertTrue(len(results) >= 1)
        print("✅ Review ro‘yxati olindi:", results)

    # ====================================================
    # 🔹 GET (DETAIL)
    # ====================================================
    def test_get_review_detail(self):
        url = reverse('review-detail', args=[self.review.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], self.review.comment)
        print("✅ Review tafsiloti olindi:", response.data)

    # ====================================================
    # 🔹 DELETE
    # ====================================================
    def test_delete_review(self):
        url = reverse('review-detail', args=[self.review.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        exists = Review.objects.filter(id=self.review.id).exists()
        self.assertFalse(exists)
        print(f"✅ Review ID={self.review.id} muvaffaqiyatli o‘chirildi.")

    # ====================================================
    # 🔹 FILTER (book bo‘yicha)
    # ====================================================
    def test_filter_reviews_by_book(self):
        response = self.client.get(self.list_url, {'book': str(self.book.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertTrue(all(str(r['book']) == str(self.book.id) for r in results))
        print("✅ Kitob bo‘yicha filter ishladi:", results)

    # ====================================================
    # 🔹 ORDERING (rating bo‘yicha)
    # ====================================================
    def test_order_reviews_by_rating(self):
        response = self.client.get(self.list_url, {'ordering': '-rating'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("✅ Reviewlar rating bo‘yicha tartiblandi:", response.data)

    # ====================================================
    # 🔹 SERIALIZER FIELDS
    # ====================================================
    def test_serializer_fields(self):
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = self.user

        serializer = ReviewSerializer(self.review, context={'request': request})
        data = serializer.data

        self.assertIn('user', data)
        self.assertIn('book', data)
        self.assertIn('rating', data)
        self.assertIn('comment', data)
        self.assertIn('is_liked', data)
        print("✅ Serializer fieldlari to‘g‘ri chiqdi:", data.keys())