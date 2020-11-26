from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.views.generic import ListView
from django.core.mail import send_mail
from taggit.models import Tag



from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, SearchForm



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



    paginator = Paginator(object_list,3) # 3 post per each page
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

    # List of similar post
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    template = 'blog/post/detail.html'
    context = {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'similar_posts': similar_posts,
    }
    return render(request, template, context)

# Search View
def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.published.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)).filter(search=search_query).order_by('-rank')
    
    context = {
        'form':form,
        'query': query,
        'results': results,
    }
    
    return render(request, 'blog/post/search.html', context)