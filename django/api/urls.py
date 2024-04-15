from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter
from .views import PostListViewSet, TagsViewSet, set_star, DraftsViewSet, ImageView, VideoView, my_posts, LastNews, CategoryViewSet


urlpatterns = [
    path('my-posts/', my_posts, name='my_posts'),
    path('posts/<uuid:pk>/set-star/<int:star>/', set_star, name='set_star'),
    path('images/<uuid:pk>/', ImageView.as_view(), name='image-view'),
    path('videos/<uuid:pk>/', VideoView.as_view(), name='video-view'),
    path('', LastNews.as_view(), name='last_news'  )
]

router = SimpleRouter()

router.register("drafts", DraftsViewSet, basename="drafts")
router.register("tags", TagsViewSet, basename="tags")
router.register("posts", PostListViewSet, basename="posts")
router.register("categories", CategoryViewSet, basename="categories")


urlpatterns += router.urls

