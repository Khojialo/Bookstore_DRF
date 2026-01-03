from rest_framework.test import APITestCase
from jigar_bookstore.models import User, Author, Category, Book, Review
from jigar_bookstore.serializers import BookSerializer, ReviewSerializer
from rest_framework.test import APIRequestFactory



class BookSerializerTestCase(APITestCase):
    def test_book_serializer(self):
        author = Author.objects.create(full_name='Chingiz Aytmatov', biography='Qirg‘iz yozuvchisi')
        category = Category.objects.create(name='Roman')

        book1 = Book.objects.create(
            title='Asrga tatigulik kun',
            author=author, category=category,
            price=50000, isbn='9781234567890'
        )
        book2 = Book.objects.create(
            title='Jamila',
            author=author, category=category,
            price=35000, isbn='9781234567891'
        )
        serializer = BookSerializer([book1, book2], many=True)

        print("\n🔹 BookSerializer chiqishi:")
        print(serializer.data)

        self.assertEqual(len(serializer.data), 2)
        self.assertEqual(serializer.data[0]['title'], 'Asrga tatigulik kun')
        self.assertEqual(serializer.data[1]['title'], 'Jamila')
        print("✅ BookSerializer testi to‘g‘ri ishladi!\n")


class ReviewSerializerTestCase(APITestCase):
    def test_review_serializer(self):
        factory = APIRequestFactory()

        user = User.objects.create_user(username='ali', email='ali@example.com', password='1234')
        author = Author.objects.create(full_name='Orhan Pamuk')
        category = Category.objects.create(name='Dramatik')
        book = Book.objects.create(title='Qor', author=author, category=category, price=45000, isbn='9786543210987')

        review = Review.objects.create(user=user, book=book, rating=5, comment='Ajoyib kitob!')

        # 👉 Soxta request yaratamiz va unga foydalanuvchini biriktiramiz
        request = factory.get('/')
        request.user = user

        # Serializerga context sifatida requestni beramiz
        serializer = ReviewSerializer(review, context={'request': request})

        print("🔹 ReviewSerializer chiqishi:")
        print(serializer.data)

        self.assertEqual(serializer.data['rating'], 5)
        self.assertEqual(serializer.data['comment'], 'Ajoyib kitob!')
        self.assertEqual(serializer.data['book'], book.id)
        self.assertEqual(serializer.data['user'], user.id)
        print("✅ ReviewSerializer testi to‘g‘ri ishladi!\n")
