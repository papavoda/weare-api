from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter
from .views import PostListViewSet, TagsViewSet, SetStar , DraftsViewSet, ImageView, VideoView, MyPosts, LastNews, CategoryViewSet


urlpatterns = [
    path('my-posts/', MyPosts.as_view(), name='my_posts'),
    path('posts/<uuid:pk>/set-star/', SetStar.as_view(), name='set_star'),
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

