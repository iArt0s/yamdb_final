from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from users.models import User


class Genre(models.Model):
    """Модель для сортировки произведений по жанрам."""

    name = models.CharField(
        max_length=256,
        verbose_name='Жанр',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Идентификатор жанра',
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель для сортировки произведений по категориям."""

    name = models.CharField(
        max_length=256,
        verbose_name='Название категории',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Идентификатор категории',
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель для объявления произведений."""

    name = models.CharField(
        max_length=100,
        verbose_name='Название произведения',
    )
    year = models.IntegerField(
        verbose_name='Дата выхода произведения',
    )
    description = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='Краткое содержание',
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр произведения',
        null=True,
        related_name='genres',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        verbose_name='Категория произведения',
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name

    def validate_year(self):
        """Метод, позволяющий отследить корректный год выпуска произведения."""
        if self > timezone.now().year:
            raise ValidationError(
                {'year': ('Год выпуска не может быть в будущем!')}
            )


class Review(models.Model):
    """Модель для обработки отзызвов к произведениям."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField('Текст')
    score = models.IntegerField(
        'Оценка',
        validators=[
            MinValueValidator(1, 'Оценка должна быть от 1 до 10!'),
            MaxValueValidator(10, 'Оценка должна быть от 1 до 10!')
        ]
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='nonunique_review_constraint'
            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель для обработки комментариев к отызвам."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-pub_date']

    def __str__(self):
        return self.text
