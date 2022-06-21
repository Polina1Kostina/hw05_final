from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


posts_per_page: int = 10


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.select_related('author')
    paginator = Paginator(posts, posts_per_page)
    page_mumber = request.GET.get('page')
    page_obj = paginator.get_page(page_mumber)
    context = {
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.post.select_related('group')
    paginator = Paginator(posts, posts_per_page)
    page_mumber = request.GET.get('page')
    page_obj = paginator.get_page(page_mumber)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context, slug)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.name.select_related('author')
    paginator = Paginator(posts, posts_per_page)
    page_mumber = request.GET.get('page')
    page_obj = paginator.get_page(page_mumber)
    if request.user.is_authenticated:
        follower = Follow.objects.filter(user=request.user, author=author)
        if follower.exists():
            following = True
        else:
            following = False
    else:
        following = None
    context = {
        'posts': posts,
        'page_obj': page_obj,
        'author': author,
        'following': following
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    posts = get_object_or_404(Post, id=post_id)
    post_cnt = Post.objects.filter(
        author=posts.author).count()
    comments = posts.comments.select_related('post')
    form = CommentForm(request.POST or None)
    context = {
        'posts': posts,
        'post_cnt': post_cnt,
        'comments': comments,
        'form': form

    }
    return render(request, template, context, post_id)


@login_required()
def post_create(request):
    template = 'posts/post_create.html'
    form = PostForm(request.POST)
    context = {
        'form': form
    }
    username = request.user.get_username()
    if request.method != 'POST':
        form = PostForm()
        return render(request, template, context)
    if form.is_valid():
        form.save(commit=False)
        form.instance.author = request.user
        form.save()
        return redirect('posts:profile', username)
    return render(request, template, context)


@login_required()
def post_edit(request, post_id):
    template = 'posts/post_create.html'
    posts = Post.objects.get(pk=post_id)
    is_edit = True
    form = PostForm(instance=posts)
    context = {
        'posts': posts,
        'is_edit': is_edit,
        'form': form
    }
    if request.user != posts.author:
        return redirect('posts:post_detail', post_id)
    if request.method != 'POST':
        return render(request, template, context, post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=posts
    )
    if not form.is_valid():
        return render(request, template, context, post_id)
    form.instance.author = request.user
    form.save()
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, posts_per_page)
    page_mumber = request.GET.get('page')
    page_obj = paginator.get_page(page_mumber)
    context = {
        'posts': posts,
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    follower = Follow.objects.filter(user=user, author=author)
    if user != author and not follower.exists():
        new_follow = Follow()
        new_follow.user = user
        new_follow.author = author
        new_follow.save()
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, author=author)
    follow.delete()
    return redirect('posts:profile', username)
