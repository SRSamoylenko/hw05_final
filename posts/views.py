from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import POSTS_PER_PAGE

from .decorators import author_access, check_author_username
from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request: HttpRequest) -> HttpResponse:
    """Return all posts ordered by date of publication."""
    posts = Post.objects.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'page': page,
    }
    return render(request, 'index.html', context)


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """Return all posts of a group specified by a slug."""
    group = get_object_or_404(Group, slug=slug)

    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'page': page,
        'group': group,
    }
    return render(request, 'group.html', context)


@login_required
def new_post(request: HttpRequest) -> HttpResponse:
    """Create new post if user is authenticated and valid data passed.
    Otherwise show error message or redirect on authentication page.
    """
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('posts:index')

    context = {
        'form': form,
    }
    return render(request, 'posts/new_post.html', context)


def profile(request, username):
    """Cтраница профиля пользователя."""
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user)

    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'person': user,
        'page': page,
    }
    return render(request, 'posts/profile.html', context)


@check_author_username
def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)

    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'posts/post.html', context)


@check_author_username
@login_required
@author_access
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post', username=username, post_id=post_id)

    context = {
        'form': form,
    }
    return render(request, 'posts/new_post.html', context)


@check_author_username
@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = post
        form.save()
    return redirect('posts:post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    authors = request.user.follower.authors()
    posts = Post.objects.filter(author__in=authors)

    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.get_or_create(
        author=author,
        user=request.user,
    )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        author=author,
        user=request.user,
    ).delete()
    return redirect('posts:profile', username=username)


def page_not_found(request, exception=None):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
