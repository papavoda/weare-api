
from rest_framework import serializers, request

from blog.models import Post, Image, Video, Tag, Category, Stars
from accounts.serializers import CustomUserSerializer


class ImageSerializer(serializers.ModelSerializer):
    # exif = serializers.JSONField(source="exif_data", binary=False)
    # image_url = serializers.SerializerMethodField('get_image_url')

    class Meta:
        model = Image
        fields = '__all__'
        # ordering = ('index_number',)  # Default ordering


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        # fields = ('id', 'name', 'description', 'thumbnail', 'thumb_select')
        fields = '__all__'


class StarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stars
        fields = ('stars',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class PostDetailSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    average_stars = serializers.DecimalField(max_digits=3, decimal_places=2, coerce_to_string=False)
    category_name = serializers.CharField(source="category.name", read_only=True)

    # Ordering images by post.images_ordering
    images = serializers.SerializerMethodField('get_images')
    def get_images(self, obj):
        qset = Image.objects.filter(post_id=obj.pk).order_by(obj.images_ordering)
        # add context={'request': request} for get abs image url
        rqst = self.context.get('request')
        serializer = ImageSerializer(qset, context={'request': rqst, }, many=True, read_only=True)
        return serializer.data

    # Ordering videos by post.videos_ordering
    videos = VideoSerializer('get_videos',  many=True, read_only=True)

    def get_videos(self, obj):
        qset = Video.objects.filter(post_id=obj.pk)
        # add context={'request': request} for get abs image url
        rqst = self.context.get('request')
        serializer = VideoSerializer(qset, context={'request': rqst, }, many=True, read_only=True)
        return serializer.data

    # videos = VideoSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        # fields = (
        #     'id', 'photo_date', 'photo_date_since', 'views', 'author', 'category', 'category_name', 'tags', 'title', 'text',
        #     'main_image', 'images_ordering',  'images', 'videos', 'audios', 'stars', 'author', 'status')
        fields = '__all__'


class PostListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    average_stars = serializers.DecimalField(max_digits=3, decimal_places=2, coerce_to_string=False)

    # stars = StarSerializer(many=True, read_only=True)

    # main_image_url = serializers.SerializerMethodField()

    # TODO make main_image as url in list view
    class Meta:
        model = Post
        fields = (
            'id', 'photo_date', 'views', 'category', 'category_name', 'created', 'title', 'main_image',
            'status', 'average_stars')  # delete 'tags'

    def get_main_image_url(self, obj):
        # obj is a Post object
        # Check if the image field is not empty
        if obj.main_image:
            # Construct the absolute URL for the image

            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.main_image.url)
        return None


# serializer for CategoryListSerializer, TagListSerializer need for posts count
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'status']


class CategoryListSerializer(serializers.ModelSerializer):
    posts = PostListSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        # fields = ('id', 'name', 'posts')
        fields = '__all__'


class CategoryDetailSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        # fields = ('id', 'name', 'posts',)
        fields = '__all__'

    # def to_representation(self, instance):
    #     self.fields['children'] = CategoryDetailSerializer(many=True, read_only=True)
    #     return super(CategoryDetailSerializer, self).to_representation(instance)


#  For TagSerializer

class TagListSerializer(serializers.ModelSerializer):
    post = PostSerializer(many=True, read_only=True)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'post')


class TagDetailSerializer(serializers.ModelSerializer):
    # Working only "post", because related_name="post"
    post = PostSerializer(many=True, read_only=True)

    class Meta:
        model = Tag
        fields = ['id', 'name', 'post']
