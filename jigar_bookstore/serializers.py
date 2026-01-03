from rest_framework import serializers
from .models import User, Category, Author, Book, Review, Order, OrderItem, Payment


# =======================
# 🔹 USER SERIALIZER
# =======================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone_number', 'is_seller']
        read_only_fields = ['id']


# =======================
# 🔹 CATEGORY SERIALIZER
# =======================
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


# =======================
# 🔹 AUTHOR SERIALIZER
# =======================
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


# =======================
# 🔹 BOOK SERIALIZER
# =======================
class BookSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    average_rating = serializers.FloatField(source='get_average_rating', read_only=True)

    # nested o‘qishda
    author_detail = AuthorSerializer(source='author', read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'author_detail',
            'category', 'category_detail', 'description',
            'price', 'stock', 'cover_image',
            'published_date', 'isbn', 'average_rating'
        ]


# =======================
# 🔹 REVIEW SERIALIZER
# =======================
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    user_detail = UserSerializer(source='user', read_only=True)
    book_detail = BookSerializer(source='book', read_only=True)

    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_disliked = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id','user','user_detail','book','book_detail','rating','comment',
            'likes_count','dislikes_count','is_liked','is_disliked'
        ]
        read_only_fields = ['created_at']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_dislikes_count(self, obj):
        return obj.dislikes.count()

    def get_is_liked(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and obj.likes.filter(id=user.id).exists()

    def get_is_disliked(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and obj.dislikes.filter(id=user.id).exists()

# =======================
# 🔹 ORDER ITEM SERIALIZER
# =======================
class OrderItemSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())
    book_detail = BookSerializer(source='book', read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        return obj.get_total_price()

    class Meta:
        model = OrderItem
        fields = ['id', 'book', 'book_detail', 'quantity', 'price', 'total_price']


# =======================
# 🔹 ORDER SERIALIZER
# =======================
class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_detail = UserSerializer(source='user', read_only=True)
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_detail', 'is_paid', 'total_amount', 'status', 'items', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        order.calculate_total()
        return order


# =======================
# 🔹 PAYMENT SERIALIZER
# =======================
class PaymentSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    order_detail = OrderSerializer(source='order', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'order', 'order_detail', 'payment_method', 'transaction_id', 'status', 'paid_at']
