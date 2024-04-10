import os
import shutil
from django.db.models import F
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsAuthorOrReadOnly, IsPostAuthorOrAdminOrReadOnly
from django.db.models import Avg

from .paginations import SmallResultsSetPagination, StandardResultsSetPagination

from .serializers import (PostDetailSerializer, PostListSerializer, TagListSerializer, CategoryDetailSerializer,
                          ImageSerializer, VideoSerializer, CategoryListSerializer)

from blog.models import Post, Audio, Category, Tag, Stars, Image, Video
from .filters import PostFilter
from django_filters.rest_framework import DjangoFilterBackend
from blog.forms import PostForm

""" return all user posts with paginations"""


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_posts(request):
    try:
        # Retrieve all posts
        all_posts = Post.objects.filter(author_id=request.user.id)

        # Paginate the queryset
        paginator = StandardResultsSetPagination()
        paginated_posts = paginator.paginate_queryset(all_posts, request)

        # Serialize the paginated queryset
        serializer = PostListSerializer(paginated_posts, many=True, context={'request': request})

        return paginator.get_paginated_response(serializer.data, )
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyPosts(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    pagination_class = StandardResultsSetPagination
    serializer_class = PostDetailSerializer

    def get_queryset(self):
        user = self.request.user
        posts = Post.objects.select_related('category',
                                            'author').filter(author_id=user)
        # posts = Post.objects.select_related('category',
        #                                     'author').filter(author_id=user)

        return posts


class DraftsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    pagination_class = StandardResultsSetPagination
    serializer_class = PostDetailSerializer

    def get_queryset(self):
        user = self.request.user
        posts = Post.objects.select_related('category',
                                            'author').filter(author_id=user, status='draft')
        # posts = Post.objects.select_related('category',
        #                                     'author').filter(author_id=user)

        return posts

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Handle updating tags separately
        tags_data = request.data.getlist('tags')  # Using getlist()!!!!!!
        if tags_data is not None:
            instance.tags.set(tags_data)

        # images
        images_data = request.FILES.getlist('images')
        if images_data is not None:
            for img in images_data:
                Image.objects.create(post_id=instance.id, file=img)

        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    pagination_class = StandardResultsSetPagination
    serializer_class = CategoryDetailSerializer

    def get_queryset(self):
        return Category.objects.all()


class TagListViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    pagination_class = StandardResultsSetPagination
    serializer_class = TagListSerializer

    def get_queryset(self):
        queryset = Tag.objects.all()
        return queryset


class PostListViewSet(viewsets.ModelViewSet):
    # lookup_field = 'slug'
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter
    # Using different serializer for list (list of posts) and retrieve (single detailed post)
    serializer_classes = {
        'list': PostListSerializer,
        'retrieve': PostDetailSerializer,
        'partial_update': PostDetailSerializer,
        'update': PostDetailSerializer,
    }
    default_serializer_class = PostListSerializer  # Your default serializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def get_queryset(self):
        user = self.request.user
        # return 3 last news for home page
        if self.basename == 'home':
            queryset = Post.objects.select_related('category',
                                                   'author', ).filter(status='published').order_by('-created')[:9]

        else:
            queryset = Post.objects.select_related('category',
                                                   'author').filter(status='published').order_by('photo_date')

        return queryset

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        # increase post.views by 1
        obj.views = obj.views + 1
        obj.save(update_fields=("views",))
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        permission_classes = [IsAuthenticated, ]
        instance = self.get_object()
        if instance.author != request.user:
            raise PermissionDenied("You are not allowed to delete this post.")

        if instance.main_image:
            # Get the directory path
            main_image_directory = os.path.dirname(instance.main_image.path)
            post_directory = os.path.dirname(main_image_directory)

            # Delete post the directory
            if os.path.exists(post_directory):
                shutil.rmtree(post_directory)

            # Delete the image field
            # instance.main_image.delete()
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Handle updating tags separately
        tags_data = request.data.getlist('tags')  # Using getlist()!!!!!!
        if tags_data is not None:
            instance.tags.set(tags_data)

        media = ['images', 'videos']

        images_data = request.FILES.getlist('images')
        if images_data is not None:
            for img in images_data:
                Image.objects.create(post_id=instance.id, file=img)

        video_data = request.FILES.getlist('videos')
        if video_data is not None:
            for vid in video_data:
                Video.objects.create(post_id=instance.id, file=vid)

        return Response(serializer.data)


# categories/<uuid:category_id>/posts
class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    serializer_class = PostListSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        # KOSLTYLI
        cat = str(self.request).split('/')[-4]

        # category list
        if cat == 'categories':
            queryset = Post.objects.filter(category_id=pk, status='published').order_by('photo_date')
        # tags_list
        elif cat == 'tags':
            queryset = Post.objects.filter(tags=pk, status='published').order_by('photo_date')
        else:
            raise Exception("Wrong Tags or Category type.")
        return queryset


# TODO check if user, not author may delete media
class ImageView(APIView):
    permission_classes = [IsAuthenticated, IsPostAuthorOrAdminOrReadOnly, ]

    def get(self, request, pk):
        try:
            image = Image.objects.get(pk=pk)
            serializer = ImageSerializer(image)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Image.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk):

        try:
            image = Image.objects.get(pk=pk)
        except Image.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
        if image.post.author_id == request.user.id or request.user.is_staff:
            serializer = ImageSerializer(image, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': f'User {request.user} is not author of this media'}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk):
        # check image exist
        try:
            image = Image.objects.get(pk=pk)
        except Image.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
        # check if user author of post or admin
        if image.post.author_id == request.user.id or request.user.is_staff:
            image.delete()
            return Response({'message': 'Image deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': f'User {request.user} is not author of this media'}, status=status.HTTP_403_FORBIDDEN)


    # def delete (self, request):
    #     image_ids = request.data.get('image_ids', [])
    #     if not image_ids:
    #         return Response({"detail": "No image IDs provided."}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     deleted_count = 0
    #     # for image_id in image_ids:
    #     #     try:
    #     #         image = Image.objects.get(pk=image_id)
    #     #     except Image.DoesNotExist:
    #     #         continue  # Skip if image doesn't exist
    #     #
    #     #     # Check if the user is authorized to delete the image
    #     #     if not request.user.is_staff and image.post.author != request.user:
    #     #         continue  # Skip if user is not authorized
    #     #
    #     #     image.delete()
    #     #     deleted_count += 1
    #
    #     return Response({"detail": f"{deleted_count} images deleted successfully."},
    #                     status=status.HTTP_204_NO_CONTENT)
#
class VideoView(APIView):
    permission_classes = [IsAuthenticated, IsPostAuthorOrAdminOrReadOnly, ]

    def get(self, request, pk):
        try:
            video = Video.objects.get(pk=pk)
            serializer = VideoSerializer(video)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Video.DoesNotExist:
            return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk):

        try:
            video = Video.objects.get(pk=pk)
            serializer = VideoSerializer(video, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Video.DoesNotExist:
            return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        # check image exist
        try:
            video = Video.objects.get(pk=pk)
        except Video.DoesNotExist:
            return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)
        # check if user author of post or admin
        if video.post.author_id == request.user.id or request.user.is_staff:
            video.delete()
            return Response({'message': 'Video deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': f'User {request.user} is not author of this media'},
                            status=status.HTTP_403_FORBIDDEN)



""" New post creation """


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_create(request):
    message = 'Post created successfully.'
    form = PostForm(request.POST, request.FILES)
    post_id_returned = ''

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        post.tags.set(request.POST.getlist('tags'))

        for img in request.FILES.getlist('images'):
            # image = Image.objects.create(post_id=post.id, image=img)
            Image.objects.create(post_id=post.id, file=img)

        for video in request.FILES.getlist('videos'):
            # image = Image.objects.create(post_id=post.id, image=img)
            Video.objects.create(post_id=post.id, file=video)

        post_id_returned = post.id
        stars = Stars.objects.create(post_id=post.id, user=post.author)
        stars.save()


    else:
        message = form.errors.as_json(escape_html=True)
    return JsonResponse({'message': message, 'post_id': post_id_returned}, safe=False)


""" Update post """

# @api_view(['PUT'])
# def post_update(request, pk):
#     message = f'Post {pk} updated'
#     return JsonResponse({'message': message})


""" Set STAR to post. Only in PostDetail """


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_star(request, pk, star):
    post = Post.objects.get(pk=pk)
    if 0 < star < 6:
        stars = Stars.objects.select_related('post', 'user').filter(post_id=post.id, user=request.user)
        if stars:
            # Update if exist
            Stars.objects.filter(post_id=post.id, user=request.user).update(post_id=post.id, user=request.user,
                                                                            stars=star)
            # stars.update()
        else:
            # create if not
            stars = Stars.objects.create(post_id=post.id, user=request.user, stars=star)
            stars.save()

        average_stars = post.stars.aggregate(Avg('stars'))['stars__avg']
        # Update the average_stars field of the associated Post
        post.average_stars = average_stars
        post.save(update_fields=['average_stars'])

    return JsonResponse({'post': pk, 'average_stars': post.average_stars}, safe=False)


""" Delete post (only if user is Author)"""


# TODO delete files created with ffmpeg
# @api_view(['DELETE'])
# def post_delete(request, pk):
#     message = ''
#     post = Post.objects.get(pk=pk)
#     if post.author == request.user:
#         post.delete()
#         message = f'post {pk} deleted'
#     else:
#         raise PermissionDenied("You are not allowed to delete this post.")
#     return JsonResponse({'message': message, 'post_id': pk})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tag_create(request, tag):
    tag = Tag.objects.create(name=tag)
    tag.save()
    return JsonResponse({'message': f'Tag {tag.name} created'})


# https://django-treebeard.readthedocs.io/en/latest/tutorial.html
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_cats(request):
    cats = Category.objects.all()
    serializer = CategoryDetailSerializer(cats, many=True)
    return Response(serializer.data)


# create new categories
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_category(request):
    get = lambda node_id: Category.objects.get(pk=node_id)
    data = request.data
    root = data['root']
    name = data['name']
    if not root:
        Category.add_root(name=name)
    else:
        try:
            cat_root = Category.objects.get(name=root)
        except Category.DoesNotExist:
            return JsonResponse({'message': f'Root category with name {root} not exist'}, status=400)
        if cat_root:
            get(cat_root.pk).add_child(name=name)

    return JsonResponse({'message': f'Category {name} created'}, status=201)

