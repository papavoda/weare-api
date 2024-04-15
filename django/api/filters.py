# filters.py
import django_filters
from blog.models import Post


# https://ilyachch.gitbook.io/django-rest-framework-russian-documentation/overview/navigaciya-po-api/filtering
class PostFilter(django_filters.FilterSet):
    # Define filter fields based on your model's attributes
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    author = django_filters.CharFilter(field_name='author__name', lookup_expr='icontains')
    tag = django_filters.CharFilter(field_name='tags__name', lookup_expr='icontains')

    class Meta:
        model = Post
        fields = ['title', 'author']  # Add more fields as needed
