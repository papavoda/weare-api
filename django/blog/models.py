import os
import uuid
from io import BytesIO

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.timesince import timesince
from treebeard.mp_tree import MP_Node
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from config import settings
from blog.services.utils import resize_image, get_exif, create_video_thumbs
from accounts.models import CustomUser

from blog.services.validators import validate_image_extension, validate_video_extension


# Категории.
# https://django-treebeard.readthedocs.io/en/latest/index.html
class Category(MP_Node):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(max_length=100)

    node_order_by = ['name']


    def __str__(self):
        return 'Category: {}'.format(self.name)


# Метки
class Tag(models.Model):
    id = models.UUIDField(  # new
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(max_length=100)

    # def get_absolute_url(self):
    #     return reverse('tag_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name


# For post upload
def upload_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'upload/{instance.category.name}/{instance.photo_date}-{instance.id}/main_image/{filename}'


# Пост
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='blog_posts',
                               verbose_name='Автор')
    category = models.ForeignKey(Category, related_name="posts", verbose_name='Категория',
                                 help_text='Выберите категорию',
                                 on_delete=models.CASCADE,
                                 null=True,
                                 )

    title = models.CharField(max_length=500)
    main_image = models.ImageField(upload_to=upload_directory_path, validators=[validate_image_extension], verbose_name='Главное изображение',)
    text = models.TextField(max_length=8000, null=True, blank=True, verbose_name='Основной текст', )
    tags = models.ManyToManyField(Tag, verbose_name='Метки', related_name="post", blank=True)
    photo_date = models.DateField(auto_now=False, auto_now_add=False, verbose_name='Дата фотосъемки', )
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES,
                              default='draft')
    MEDIA_ORDERING_CHOICES = {
        ('file', 'Filename'),
        ('index_number', 'Index'),
        ('name', 'Name'),
    }
    views = models.BigIntegerField(default=0, null=True, blank=True, verbose_name='Количество просмотров', )
    images_ordering = models.CharField(max_length=30, choices=MEDIA_ORDERING_CHOICES, default='file')
    videos_ordering = models.CharField(max_length=30, choices=MEDIA_ORDERING_CHOICES, default='file')
    average_stars = models.DecimalField(_('Average Stars'), max_digits=3, decimal_places=2, default=0.00, blank=True, null=True)

    # rates_counts = blabla

    def __str__(self):
        return f'{self.category} - {self.title}'

    def photo_date_since(self):
        return timesince(self.photo_date)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.main_image:
            image_path = self.main_image.path
            resize_image(image_path, max_size=(500, 500))

    # class Meta:
    #     ordering = ('photo_date', )
class Stars(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='stars')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    STARS_CHOICES = [(i, i) for i in range(1, 6)]
    stars = models.PositiveSmallIntegerField(_('Stars'), default=3, choices=STARS_CHOICES, blank=True, null=True)
    # TODO create field that computing average star rate. Everytime while def save




# for Image upload
def image_directory(instance, filename):
    return f'upload/{instance.post.category.name}/{instance.post.photo_date}-{instance.post.id}/{filename}'


def video_directory(instance, filename):
    return f'upload/{instance.post.category.name}/{instance.post.photo_date}-{instance.post.id}/video/{filename}'


# Фото
class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    index_number = models.SmallIntegerField(_('Порядковый номер'), default=0, blank=True, null=True)
    name = models.CharField(max_length=250, null=True, blank=True)  # alt
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    file = models.ImageField(upload_to=image_directory, max_length=250)
    description = models.CharField(max_length=500, blank=True, null=True)
    validators = [validate_image_extension]
    exif_data = models.JSONField(null=True, blank=True, default=dict, )

    def __str__(self):
        return f'{self.id}'

    # class Meta:
    #     ordering = ('image',)

    def save(self, *args, **kwargs):
        # Start Get the exif data from the uploaded image
        self.exif_data = get_exif(self.file)
        super().save(*args, **kwargs)

        if self.file:
            image_path = self.file.path
            resize_image(image_path, max_size=(300, 300))
            resize_image(image_path)
            resize_image(image_path, max_size=(1200, 1200))


# Video
class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    THUMB_CHOICES = (
        ('--start.jpg', 'start'),
        ('--mid.jpg', 'mid'),
        ('--end.jpg', 'end'),
    )

    name = models.CharField(max_length=500, default='', blank=True, null=True)
    index_number = models.PositiveIntegerField(
        _('Порядковый номер'), default=0,  blank=True, null=True,)
    post = models.ForeignKey(Post, related_name='videos', on_delete=models.CASCADE, null=True)
    file = models.FileField(upload_to=video_directory, validators=[validate_video_extension])
    thumbnail = models.ImageField(upload_to=video_directory, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    validators = [FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])]
    thumb_select = models.CharField(max_length=15,
                                    choices=THUMB_CHOICES,
                                    default='--start.jpg')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.file:
            create_video_thumbs(self.file.path)


#  Audio
class Audio(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    post = models.ForeignKey(Post, related_name='audios', on_delete=models.SET_NULL, null=True)
    audio = models.FileField(upload_to=video_directory)

    def __str__(self):
        if self.name:
            return self.name


# File for another reasons
class File(models.Model):
    pass
