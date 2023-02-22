from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title
from users.models import User

from api_yamdb.settings import EMAIL_ADMIN

from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet
from .permissions import IsAdminOrReadOnly, IsOnlyAdmin, IsReviewAndComment
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, RegisterSerializer,
                          ReviewSerializer, SelfUserSerializer,
                          TitleGetSerializer, TitlePostSerializer,
                          UserSerializer, VerifySerializer)


class GenreViewSet(ListCreateDestroyViewSet):
    """Набор представлений для обработки экземпляров модели Genre."""
    queryset = Genre.objects.all()
    lookup_field = ('slug')
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(ListCreateDestroyViewSet):
    """Набор представлений для обработки экземпляров модели Category."""
    queryset = Category.objects.all()
    lookup_field = ('slug')
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    """Набор представлений для обработки экземпляров модели Title."""
    serializer_class = TitlePostSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return TitlePostSerializer

        return TitleGetSerializer

    def get_queryset(self):
        if self.action in ('retrieve', 'list'):
            return Title.objects.prefetch_related(
                'reviews').all().annotate(rating=Avg('reviews__score'))

        return Title.objects.all()


class RegisterView(viewsets.ModelViewSet):
    """Набор представлений для обработки регистрации пользователей."""
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.get(email=serializer.data['email'])
        user.is_active = False
        user.save()
        token = default_token_generator.make_token(user)
        send_mail(
            subject=f'Привет {user.username} ! Код для получения токена.',
            message=f'Код: {token}',
            from_email=EMAIL_ADMIN,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyUserView(generics.GenericAPIView):
    """Обработчик для проверки аутентификации пользователей."""
    permission_classes = (permissions.AllowAny,)
    serializer_class = VerifySerializer

    def post(self, serializer):
        verify_code = serializer.data.get('confirmation_code')
        if serializer.data == {}:
            return Response({'error': 'Запрос без параметров'},
                            status=status.HTTP_400_BAD_REQUEST)
        if 'username' not in serializer.data:
            return Response({'error': 'Запрос без username'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(
            User, username=serializer.data.get('username'))
        if not default_token_generator.check_token(user, verify_code):
            return Response({'error': 'Код подтверждения неверный!'},
                            status=status.HTTP_400_BAD_REQUEST)
        user.is_active = True
        user.save()
        refresh = RefreshToken.for_user(user)

        return Response({'access': str(refresh.access_token)},
                        status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """Набор представлений для обработки экземпляров модели User."""
    queryset = User.objects.all()
    permission_classes = (IsOnlyAdmin,)
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    lookup_field = ('username')
    search_fields = ('=username',)

    @action(
        detail=False,
        methods=['patch', 'get'],
        url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def self_user(self, request):
        user = self.request.user
        if request.method == 'GET':
            serializer = SelfUserSerializer(user)

            return Response(serializer.data)

        serializer = SelfUserSerializer(
            self.request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):
    """Набор представлений для обработки экземпляров модели Review."""
    serializer_class = ReviewSerializer
    permission_classes = (
        IsReviewAndComment, permissions.IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Набор представлений для обработки экземпляров модели Comment."""
    serializer_class = CommentSerializer
    permission_classes = (
        IsReviewAndComment, permissions.IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)
