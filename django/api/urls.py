from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter
from .views import PostListViewSet, CategoryViewSet, TagListViewSet, post_create, set_star, tag_create, CategoryViewSet, \
    PostViewSet, DraftsViewSet, ImageView, VideoView, my_posts, get_cats, create_category

router = SimpleRouter()
router.register(r'posts', PostViewSet, basename='post_list')

urlpatterns = [
    path('categories/create/', create_category, name='create-category'),
    path('get-cats/', get_cats, name='get_cats'),
    path('my-posts/', my_posts, name='my_posts'),
    path('post-create/', post_create, name='post_create'),
    # path('posts/<uuid:pk>/delete/', post_delete, name='post_delete'),
    path('posts/<uuid:pk>/set-star/<int:star>/', set_star, name='set_star'),
    path('tag-create/<str:tag>/', tag_create, name='tag_create'),
    path('tags/<uuid:pk>/', include(router.urls)),
    path('categories/<uuid:pk>/', include(router.urls)),
    path('images/<uuid:image_id>/', ImageView.as_view(), name='image-view'),
    path('videos/<uuid:image_id>/', VideoView.as_view(), name='video-view'),
]

router = SimpleRouter()

router.register("drafts", DraftsViewSet, basename="drafts")
router.register("categories", CategoryViewSet, basename="categories")
router.register("tags", TagListViewSet, basename="tags")
router.register("posts", PostListViewSet, basename="posts")
router.register("", PostListViewSet, basename="home")


urlpatterns += router.urls

