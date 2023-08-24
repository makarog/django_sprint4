from blog.models import Comment
from core.constants import POST_ON_MAIN
from core.utils import get_post_data
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View


class MixinListView:
    ordering = '-pub_date'
    paginate_by = POST_ON_MAIN


class CommentMixinView(LoginRequiredMixin, View):
    """Mixin для редактирования и удаления комментария.

    Атрибуты:
        - pk_url_kwarg: Имя URL-параметра, содержащего идентификатор
        комментария.

    Методы:
        - dispatch(request, *args, **kwargs): Проверяет, является ли
        пользователь автором комментария.
        - get_success_url(): Возвращает URL-адрес перенаправления после
        успешного редактирования или удаления комментария.
    """

    model = Comment
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_pk"
    post_pk_url_kwarg = 'pk'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", pk=self.kwargs[self.pk_url_kwarg])
        get_post_data(pk = kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        pk = self.kwargs[self.post_pk_url_kwarg]
        return reverse("blog:post_detail", kwargs={"pk": pk})
