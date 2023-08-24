from blog.models import Comment, Post
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone


def get_all_posts_queryset():
    """Вернуть все посты."""
    query_set = (
        Post.objects.select_related(
            "category",
            "location",
            "author",
        )
        .annotate(comment_count=Count("comments"))
        .order_by("-pub_date")
    )
    return query_set


def get_post_published_query():
    """Вернуть опубликованные посты."""
    query_set = get_all_posts_queryset().filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )
    return query_set


def get_post_data(pk):
    """Вернуть данные поста.

    Ограничивает возможность авторов писать и редактировать комментарии
    к постам снятым с публикации, постам в категориях снятых с публикации,
    постам дата публикации которых больше текущей даты.
    Проверяет:
        - Пост опубликован.
        - Категория в которой находится поста опубликована.
        - Дата поста не больше текущей даты.
    """
    queryset = Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )
    
    post = get_object_or_404(queryset, pk=pk)

    return post
