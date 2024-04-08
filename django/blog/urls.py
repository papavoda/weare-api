from django.urls import include, path
from .views import *

urlpatterns = [

    path('', HomeView.as_view(), name='home'),
    # path('post-create/', PostCreateFormView.as_view(), name='post_create'),
]
