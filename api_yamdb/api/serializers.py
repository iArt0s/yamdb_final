from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    (Де-)Сериализатор для модели User приложения users.
    Регистрация пользователей.
    """

    class Meta:
        model = User
        fields = ['email', 'username']

    def validate(self, data):
        if 'me' == data['username']:
            raise serializers.ValidationError(
                'Нельзя создать пользователя с username "me" ')
        return data


class VerifySerializer(serializers.ModelSerializer):
    """(Де-)Сериализатор для модели User приложения users. Аутентификация."""
    class Meta:
        model = User
        fields = ['username', 'confirmation_code']


class GenreSerializer(serializers.ModelSerializer):
    """(Де-)Сериализатор для модели Genre приложения reviews."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    """(Де-)Сериализатор для модели Category приложения reviews."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitlePostSerializer(serializers.ModelSerializer):
    """Стандартный (де-)сериализатор для модели Title приложения reviews."""

    genre = SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all()
    )
    category = SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'


class TitleGetSerializer(serializers.ModelSerializer):
    """
    (Де-)Сериализатор для модели Title приложения reviews,
    использующий вложенные сериализаторы.
    Цель использоваия - получение  вместе с объектом Title
    списка, состоящего из привязанных к нему объектов Genre и Category
    вместо ссылок на данные объекты.
    """
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class SelfUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        read_only_fields = ('role',)


class CurrentTitleDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context.get('view').kwargs.get('title_id')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзывов."""
    author = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    title = serializers.HiddenField(default=CurrentTitleDefault())

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        model = Review
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=['title', 'author']
            )
        ]


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев."""
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
        read_only_fields = ('review',)
