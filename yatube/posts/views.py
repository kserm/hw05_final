from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Follow, Post, Group, User, Comment
from .forms import PostForm, CommentForm
from .paginator import pagination


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.all()
    page_obj = pagination(request, post_list, settings.POSTS_NUM)
    return render(request, 'posts/index.html', {'page_obj': page_obj})


def group_posts(request, slug: str):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group)
    page_obj = pagination(request, post_list, settings.POSTS_NUM)
    return render(request, 'posts/group_list.html', {'group': group,
                                                     'page_obj': page_obj})


def profile(request, username: str):
    user = request.user
    author = User.objects.get(username=username)
    post_list = Post.objects.filter(author=author)
    following = False
    if user.is_authenticated:
        is_following = Follow.objects.filter(user=user, author=author)
        if is_following.exists():
            following = True
    else:
        following = False
    page_obj = pagination(request, post_list, settings.POSTS_NUM)
    context = {
        'username': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id: int):
    post = Post.objects.get(pk=post_id)
    form = CommentForm()
    comments = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(
            request.POST,
            files=request.FILES or None,
        )
        if form.is_valid():
            user = request.user
            form.instance.author = user
            form.save()
            return redirect(f'/profile/{user.username}/')
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id: int):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
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
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    authors = []
    follow = Follow.objects.filter(user=request.user)
    for obj in follow:
        authors.append(obj.author)
    post_list = Post.objects.filter(author__in=authors)
    page_obj = pagination(request, post_list, settings.POSTS_NUM)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    if user != author and Follow.objects.filter(user=user,
                                                author=author).count() == 0:
        Follow.objects.create(user=user, author=author)
    return redirect(f'/profile/{author}/')


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    if user != author:
        Follow.objects.filter(user=user, author=author).delete()
    return redirect(f'/profile/{author}/')
