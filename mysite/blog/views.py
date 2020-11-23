from django.http import request
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from taggit.models import Tag

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm



# Create your views here.


# Class based Post List View
class PostListView(ListView):
    template_name= 'blog/post/list.html'
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 1



# Function based Post list View
def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])



    paginator = Paginator(object_list,1) # 3 post per each page
    page = request.GET.get('page')




    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    context = {
        'page': page,
        'posts': posts,
        'tag': tag,
    }
    return render(request, 'blog/post/list.html', context)


# Share post with emails
def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n"f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'ceasarkwadwo@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    context = {
        'post':post,
        'form': form,
        'sent': sent,
    }
    return render(request, 'blog/post/share.html', context)


# Post Detail View
def post_detail(request, year, day, month, post):
    post = get_object_or_404(Post, slug=post, 
                                    status='published',
                                   publish__year = year,
                                    publish__month=month,
                                    publish__day =day)
    
    # Lis to of active comments
    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    template = 'blog/post/detail.html'
    context = {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
    }
    return render(request, template, context)