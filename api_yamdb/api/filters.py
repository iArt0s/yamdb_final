from django_filters import CharFilter
from django_filters import rest_framework as filters
from reviews.models import Title


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class TitleFilter(filters.FilterSet):
    """Настройка фильтрации по частичным совпадениям."""
    genre = CharFilterInFilter(field_name='genre__slug', lookup_expr='in')
    category = CharFilterInFilter(field_name='category__slug',
                                  lookup_expr='in')
    name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ['genre', 'category', 'name', 'year', ]
