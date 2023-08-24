from core.mixins import CommentMixinView, MixinListView
from core.utils import get_all_posts_queryset, get_post_data
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.timezone import now
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentEditForm, PostEditForm, UserEditForm
from .models import Category, Comment, Post, User


class MainPostListView(MixinListView, ListView):
    """Главная страница со списком постов. """

    model = Post
    template_name = "blog/index.html"

    def get_queryset(self):
        query_set = get_all_posts_queryset().filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
        return query_set


class CategoryPostListView(MixinListView, ListView):
    """Страница со списком постов выбранной категории."""

    template_name = "blog/category.html"
    category = None

    def get_queryset(self):
        slug = self.kwargs["category_slug"]
        self.category = get_object_or_404(
            Category, slug=slug, is_published=True
        )
        query_set = get_all_posts_queryset().filter(
            category=self.category,
            pub_date__lte=timezone.now(),
            is_published=True
        )
        return query_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class UserPostsListView(MainPostListView):
    """Страница со списком постов пользователя."""

    template_name = "blog/profile.html"
    author = None

    def get_queryset(self):
        username = self.kwargs["username"]
        self.author = get_object_or_404(
            User.objects.prefetch_related(Prefetch(
                'authors',
                queryset=get_all_posts_queryset().filter(
                    Q(author__username=self.request.user.username)
                    | Q(is_published=True)
                    & Q(category__is_published=True)
                    & Q(pub_date__lte=timezone.now())
                )
            )), username=username
        )
        return self.author.authors.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.author
        return context


class PostDetailView(DetailView):
    """Страница выбранного поста."""

    model = Post
    template_name = "blog/detail.html"
    post_data = None

    def get_queryset(self):
        self.post_data = get_object_or_404(
            Post, (
                Q(is_published=True)
                & Q(category__is_published=True)
                & Q(pub_date__lte=timezone.now())
                | Q(author__username=self.request.user.username)
            ), pk=self.kwargs[self.pk_url_kwarg],
        )
        return get_all_posts_queryset().filter(
            Q(is_published=True)
            | Q(author__username=self.request.user.username)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentEditForm()
        context["comments"] = self.object.comments.all().select_related(
            "author"
        )
        return context

    def check_post_data(self):
        """Вернуть результат проверки поста."""
        return all(
            (
                self.post_data.is_published,
                self.post_data.pub_date <= now(),
                self.post_data.category.is_published,
            )
        )


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление профиля пользователя."""

    model = User
    form_class = UserEditForm
    template_name = "blog/user.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        username = self.request.user.username
        return reverse("blog:profile", kwargs={"username": username})


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание поста."""

    model = Post
    form_class = PostEditForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user
        return reverse("blog:profile", kwargs={"username": username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование поста."""

    model = Post
    form_class = PostEditForm
    template_name = "blog/create.html"

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                "blog:post_detail",
                pk=self.kwargs[self.pk_url_kwarg]
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        pk = self.kwargs[self.pk_url_kwarg]
        return reverse("blog:post_detail", kwargs={"pk": pk})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление поста."""

    model = Post
    template_name = "blog/create.html"

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                "blog:post_detail",
                pk=self.kwargs[self.pk_url_kwarg]
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostEditForm(instance=self.object)
        return context

    def get_success_url(self):
        username = self.request.user
        return reverse_lazy("blog:profile", kwargs={"username": username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария."""

    model = Comment
    form_class = CommentEditForm
    template_name = "blog/comment.html"
    post_data = None

    def dispatch(self, request, *args, **kwargs):
        self.post_data = get_post_data(pk=kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_data
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.kwargs[self.pk_url_kwarg]
        return reverse("blog:post_detail", kwargs={"pk": pk})


class CommentUpdateView(CommentMixinView, UpdateView):
    """Редактирование комментария."""

    form_class = CommentEditForm
    pk_url_kwarg = 'comment_pk'


class CommentDeleteView(CommentMixinView, DeleteView):
    """Удаление комментария.

    CommentMixinView: Базовый класс, предоставляющий функциональность.
    """
    pk_url_kwarg = 'comment_pk'
