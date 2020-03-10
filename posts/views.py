import datetime as dt

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Post, User, Group, Follow


@login_required(login_url='/auth/login')
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, instance=Post(author=request.user))
        if form.is_valid():
            form.save()
            return redirect("index")
        return render(request, "post_new.html", {"form": form, 'exist': False})
    form = PostForm()
    return render(request, "post_new.html", {"form": form, 'exist': False})


@cache_page(60 * 15)
def index(request):
    latest = Post.objects.order_by("-pub_date")[:11]
    year = dt.datetime.now().year
    paginator = Paginator(latest, 5)  # показывать по 5 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(request, "index.html", {"posts": latest, "year": year, 'paginator': paginator, 'page': page, })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date")[:12]
    paginator = Paginator(posts, 5)  # показывать по 5 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(request, "group.html", {"group": group, "posts": posts, 'paginator': paginator, 'page': page, })


def profile(request, username):
    # тут тело функции
    user_profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user_profile).order_by('-pub_date').all()
    paginator = Paginator(posts, 5)  # показывать по 5 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    followers = Follow.objects.filter(user=request.user, author=user_profile).count()
    if followers > 0:
        following = True
    else:
        following = False
    return render(request, "profile.html",
                  {'user_profile': user_profile, 'posts': posts, 'page': page, 'paginator': paginator,
                   'following': following})


def post_view(request, username, post_id):
    # тут тело функции
    profile = get_object_or_404(User, username=username)
    post = Post.objects.get(author=profile.pk, id=post_id)
    posts_count = Post.objects.filter(author=profile).order_by('-pub_date').count()
    items = post.comments.all()
    form = CommentForm()
    return render(request, "post.html",
                  {"profile": profile, "post": post, "count": posts_count, "form": form, "items": items})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = get_object_or_404(User, username=username)
    if request.user != user:
        return redirect("post", username=request.user.username, post_id=post_id)
        # добавим в form свойство files
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("post", username=request.user.username, post_id=post_id)

    return render(
        request, "post_new.html", {"form": form, "post": post},
    )
    #


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        # comments = post.comments.get().all()
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post', username=post.author.username, post_id=post_id)
    form = CommentForm()
    return redirect('post', username=post.author.username, post_id=post_id)


@login_required
def follow_index(request):
    """страница просмотра подписок"""
    # favorite_list = Follow.objects.select_related('author', 'user').filter(user=request.user)
    # author_list = [favorite.author for favorite in favorite_list]
    # post_list = Post.objects.filter(author__in=author_list).order_by("-pub_date")
    favorite_list = Follow.objects.filter(user=request.user)
    post_list = Post.objects.filter(favorite_list__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    follow = User.objects.get(username=username)
    count_follower = Follow.objects.filter(user= request.user, author=follow).count()
    if (count_follower == 0) and ( request.user.username != follow.username):
        Follow.objects.create(user= request.user, author=follow)
        return redirect("profile", username=username)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    follower = User.objects.get(username=request.user.username)
    follow = User.objects.get(username=username) #Если пользователь удалиться, то и подписка на него тоже (author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following"))
    Follow.objects.get(user=follower, author=follow).delete()
    return redirect('profile', username=username)
