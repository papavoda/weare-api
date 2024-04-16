import os
import shutil
from django.http import JsonResponse

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.views import APIView

from .permissions import IsAuthorOrReadOnly, IsPostAuthorOrAdminOrReadOnly
from django.db.models import Avg

from .paginations import SmallResultsSetPagination, StandardResultsSetPagination

from .serializers import (PostDetailSerializer, PostListSerializer, TagListSerializer,
                          ImageSerializer, VideoSerializer, CategoryListSerializer)

from blog.models import Post, Audio, Category, Tag, Stars, Image, Video
from .filters import PostFilter
from django_filters.rest_framework import DjangoFilterBackend
from blog.forms import PostForm

""" return all user posts with paginations"""
# home
class LastNews(ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = PostListSerializer

    queryset = Post.objects.select_related('category',
                                           'author', ).filter(status='published').order_by('-created')

# Child for LastNews
class MyPosts(LastNews):
    permission_classes = [IsPostAuthorOrAdminOrReadOnly, IsAuthenticated]
    def get_queryset(self,):
        queryset = Post.objects.filter(author_id=self.request.user.id)
        return queryset



class CategoryViewSet(viewsets.ModelViewSet):
    pagination_class = None
    serializer_class = CategoryListSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]  # Permission for DELETE method
        elif self.request.method == 'POST':
            return [IsAdminUser()]  # Permission for create method
        else:
            return [IsAuthenticated()]  # Default permission for other methods

    def get_queryset(self):
        queryset = Category.objects.all()
        return queryset

    def retrieve(self, request, pk):
        posts = Post.objects.select_related('category', 'author').filter(category=pk, status='published').order_by('photo_date')
        paginator = StandardResultsSetPagination()
        paginated_posts = paginator.paginate_queryset(posts, request)
        serializer = PostListSerializer(paginated_posts, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data, )

    def create(self, request):
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


class TagsViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    serializer_class = TagListSerializer
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]  # Example permission for DELETE method
        else:
            return [IsAuthenticated()]  # Default permission for other methods
    def get_queryset(self):
        queryset = Tag.objects.all()
        return queryset

    def retrieve(self, request, pk):
        posts = Post.objects.select_related('category', 'author').filter(tags=pk, status='published').order_by('photo_date')
        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(posts, request)
        serializer = PostListSerializer(paginated_posts, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data, )

    #  Create new tag
    def create(self, request):
        serializer = TagListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def destroy(self, request, pk=None):
    #     try:
    #         tag = Tag.objects.get(pk=pk)
    #     except Tag.DoesNotExist:
    #         return Response(status=status.HTTP_404_NOT_FOUND)
    #     tag.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)



class PostListViewSet(viewsets.ModelViewSet):
    # lookup_field = 'slug'
    permission_classes = [IsPostAuthorOrAdminOrReadOnly]
    # permission_classes = []
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

    def create(self, request, *args, **kwargs):
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


class DraftsViewSet(PostListViewSet):
    queryset = Post.objects.none()
    def get_queryset(self):
            user = self.request.user
            queryset = Post.objects.select_related('category',
                                                'author').filter(author_id=user, status='draft')
            return queryset


class ImageView(APIView):
    permission_classes = [IsAuthenticated, IsPostAuthorOrAdminOrReadOnly, ]
    serializer_class = ImageSerializer
    def get(self, request, pk):
        try:
            image = Image.objects.get(pk=pk)
            serializer = self.serializer_class(image)
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


class VideoView(APIView):
    permission_classes = [IsAuthenticated, IsPostAuthorOrAdminOrReadOnly, ]
    serializer_class = VideoSerializer
    def get(self, request, pk):
        try:
            video = Video.objects.get(pk=pk)
            serializer = self.serializer_class(video)
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


""" Set STAR to post. Only in PostDetail """
class SetStar(GenericAPIView):
    permission_classes = [IsAuthenticated ]
    serializer_class = PostDetailSerializer
    def post(self, request, pk,):
        post = Post.objects.get(pk=pk)
        user = request.user
        post_id = pk
        star = int(request.data.get('star'))
        if 0 < star < 6:
            stars = Stars.objects.select_related('post', 'user').filter(post_id=post_id, user=user)
            if stars:
                # Update if exist
                Stars.objects.filter(post_id=post_id, user=user).update(post_id=post_id, user=user,
                                                                                stars=star)
                # stars.update()
            else:
                # create if not
                stars = Stars.objects.create(post_id=post_id, user=user, stars=star)
                stars.save()

            average_stars = post.stars.aggregate(Avg('stars'))['stars__avg']
            # Update the average_stars field of the associated Post
            post.average_stars = average_stars
            post.save(update_fields=['average_stars'])

        serializer = self.serializer_class(post,)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return JsonResponse({'post': pk, 'average_stars': post.average_stars}, safe=False)