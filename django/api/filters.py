# filters.py
import django_filters
from blog.models import Post


# https://ilyachch.gitbook.io/django-rest-framework-russian-documentation/overview/navigaciya-po-api/filtering
class PostFilter(django_filters.FilterSet):
    # Define filter fields based on your model's attributes
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Post
        fields = ['title']  # Add more fields as needed
