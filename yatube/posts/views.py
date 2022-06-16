from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import get_page_context

User = get_user_model()


def index(request):
    context = get_page_context(
        request, Post.objects.select_related(
            'author', 'group').order_by('-pub_date'))
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    context = {
        'group': group,

    }
    context.update(get_page_context(request, group.posts.all()))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following = False
    context = {
        'author': author,
        'following': following,
    }
    context.update(get_page_context(request, author.posts.all()))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    post_comments = post.comments.all()
    form = CommentForm()
    context = {
        'author': author,
        'post': post,
        'form': form,
        'comments': post_comments,
    }

    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        username = request.user
        return redirect('posts:profile', username)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    author = post.author

    if author != user:

        return redirect('posts:post_detail', post_id)

    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    context = {
        'post': post,
        'is_edit': True,
        'form': form,
        'post_id': post_id,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        form.save()

        return redirect(reverse(
            'posts:post_detail',
            kwargs={
                'post_id': post_id}
        ))
    return redirect(reverse(
        'posts:post_detail',
        kwargs={
            'post_id': post_id}))


@login_required
def follow_index(request):
    context = {
        'is_index': False,
    }
    context.update(get_page_context(
        request, Post.objects.filter(author__following__user=request.user)))
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=user, author=author)
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)

    return redirect(reverse('posts:profile', args=[username]))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect(reverse('posts:profile', kwargs={'username': username}))


def page_not_found(request, exception):
    return render(
        request,
        'core/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request, *args, **argv):
    return render(request, "core/403.html", status=403)
