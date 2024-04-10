from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import *

from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory


class CategoryAdmin(TreeAdmin):
    # list_display = ('__all__', )
    form = movenodeform_factory(Category)


admin.site.register(Category, CategoryAdmin)

admin.site.register(Tag)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("name", "file", 'get_image')

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.file.url} width="110" height="80"')

    get_image.short_description = "Миниатюра"


class ImageInline(admin.StackedInline):
    model = Image
    max_num = 20
    extra = 0
    list_display = ("name", "file", 'get_image')
    readonly_fields = ("get_image",)

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.file.url} width="110" height="80">')


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "file", "thumb_select")


class VideoInline(admin.StackedInline):
    model = Video
    max_num = 4
    extra = 0
    list_display = ("name", "file",)


@admin.register(Stars)
class StarsAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['post', 'user', 'stars']


class StarsInline(admin.StackedInline):
    model = Stars
    extra = 0
    list_display = ['id', 'post', 'user', 'stars']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['photo_date', 'title', 'category', 'get_image', 'author', 'status', 'average_stars']
    list_editable = ['status', ]
    readonly_fields = ("get_image",)
    inlines = [ImageInline, VideoInline, StarsInline]

    # prepopulated_fields = {'slug': ('title',)}  # new

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.main_image.url} width="110" height="80">')
