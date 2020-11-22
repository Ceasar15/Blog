from django.http import request
from django.shortcuts import render, get_object_or_404
from .models import Post

# Create your views here.

# Post list View
def post_list(request):
    posts = Post.published.all()
    context = {
        'posts': posts,
    }
    return render(request, 'blog/post/list.html', context)


# Post Detail View
def post_detail(request, year, day, month, post):
    post = get_object_or_404(Post, slug=post, 
                                    status='published',
                                   publish__year = year,
                                    publish__month=month,
                                    publish__day =day)
    template = 'blog/post/detail.html'
    context = {
        'post':post,
    }
    return render(request, template, context)