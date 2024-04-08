# from typing import Any
# from django.db.models.query import QuerySet
# from django.urls import reverse
# from django.views.generic.edit import FormView
# from django.shortcuts import render
from django.views.generic import ListView, TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, Category, Image, Video
from .forms import PostCreateForm


# Create your views here.
class HomeView(TemplateView):
    #  queryset = Post.objects.all()
    template_name = 'blog/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['free_latest_posts'] = Post.objects.select_related('category', 'author').filter(
            status='published').order_by(
            '-photo_date')[:20]
        context['categories'] = Category.objects.all()
        return context


class PostCreateFormView(LoginRequiredMixin, CreateView):
    template_name = "blog/post-create.html"
    model = Post
    form_class = PostCreateForm
    success_url = "/"

    # def post(self, request, *args, **kwargs):
    #     form_class = self.get_form_class()
    #     form = self.get_form(form_class)
    #     if form.is_valid():
    #         return self.form_valid(form)
    #     else:
    #         return self.form_invalid(form)

    def form_valid(self, form):
        # print(self.request.user)
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        # upload images

        files = form.cleaned_data["images"]
        for image in files:
            Image.objects.create(post=post, image=image)
        # upload videos
        videos = form.cleaned_data["videos"]
        for video in videos:
            Video.objects.create(post=post, video=video)
        return super().form_valid(form)

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['form'] = PostCreateForm
    #     return context

# class PostCreateView(LoginRequiredMixin, CreateView):
#     template_name = 'blog/post-create.html'
#     model = Post
#     form_class = PostCreateForm

#     def form_valid(self, form):
#         post = form.save(commit=False)
#         post.author = self.request.user
#         post.save()
#         images = self.request.FILES.getlist('images')
#         for image in images:
#             Image.objects.create(post=post, image=image)
#         return super().form_valid(form)

#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['form'] = PostCreateForm
#         context['main_title'] = 'Добавление статьи'
#         context['nabr'] = 'new-post'
#         return context
