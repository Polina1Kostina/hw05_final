from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel


User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='Имя',
        max_length=200
    )
    slug = models.SlugField(
        verbose_name='Адрес',
        unique=True
    )
    description = models.TextField(verbose_name='Описание')

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Post(CreatedModel):
    text = models.TextField(verbose_name='Текст поста')
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='name'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Сообщество',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='post',
        help_text='Group to which this message belongs to',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self) -> str:
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']
        verbose_name = "Пост"
        verbose_name_plural = "Посты"


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        verbose_name='Пост',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(verbose_name='Текст комментария')

    def __str__(self) -> str:
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = "Подписки"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'), name='unique follow'
            )
        ]
