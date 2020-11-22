from django.http import request
from django.shortcuts import render, get_object_or_404
from .models import Post

# Create your views here.

def post_list(request):
    post = Post.published.all()
    context = {
        'post': post,
    }
    return (render, 'post/list.html', context)

def post_detail(request, year, day, month, post):
    post = get_object_or_404(Post, slug=post, 
                                    status='published',
                                   publish__year = year,
                                    publish__month=month,
                                    publish__day =day)
    template = 'blog/detail.html'
    context = {
        'post':post,
    }
    return (render, template, context)