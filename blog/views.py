from django.shortcuts import render
from .models import Post, Category
from django.views.generic import ListView, DetailView, View
# Create your views here.


class PostListView(ListView):
    model = Post
    template_name = 'blog/blog.html'
    context_object_name = 'posts'


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/blog_post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = Category.objects.all()
        return context
    
