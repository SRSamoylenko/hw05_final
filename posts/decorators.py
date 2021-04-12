from functools import wraps

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from posts.models import Post, User


def author_access(view_func):
    @wraps(view_func)
    def wrapped_view(request, username, post_id):
        post = get_object_or_404(Post, id=post_id)
        if request.user != post.author:
            return redirect(reverse('posts:post', kwargs={
                'post_id': post_id,
                'username': username,
            }))
        return view_func(request, username, post_id)
    return wrapped_view


def check_author_username(view_func):
    @wraps(view_func)
    def wrapped_view(request, username, post_id):
        user = get_object_or_404(User, username=username)
        post = get_object_or_404(Post, id=post_id)
        if post.author != user:
            return redirect(
                request.path,
                username=post.author.username,
                post_id=post_id
            )
        return view_func(request, username, post_id)
    return wrapped_view
