from django import forms
from .models import Post, Image, Tag


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class PostCreateForm(forms.ModelForm):
    # validators
    images = MultipleFileField(required=False, )
    videos = MultipleFileField(required=False)

    class Meta:
        model = Post
        fields = ['photo_date', 'title',
                  'category', 'tags', 'main_image', 'text', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Заголовок *', 'class': 'form-control'}),
            # 'slug': forms.TextInput(attrs={'placeholder': 'URL *', 'class': 'form-control'}),
            # 'description': forms.TextInput(attrs={'placeholder': 'Описание *', 'class': 'form-control'}),
            # 'keywords': forms.TextInput(attrs={'placeholder': 'Ключевые слова *', 'class': 'form-control'}),
            # 'intro': forms.Textarea(attrs={'placeholder': 'Интро *', 'class': 'form-control'}),
            'text ': forms.Textarea(attrs={'placeholder': 'Интро *', 'class': 'form-control'}),
            'main_image': forms.ClearableFileInput(attrs={'class': 'form-control', 'multiple': False}),

        }


class PostForm(forms.ModelForm):
    images = MultipleFileField(required=False, )
    # tags = []
    class Meta:
        model = Post
        fields = ['photo_date', 'title',
                  'category', 'tags', 'main_image', 'text', 'status', ]


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ('name', )
