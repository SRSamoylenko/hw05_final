from typing import Optional

from django.contrib.auth import get_user_model
from django.db import models

from yatube.utils import wrap_text

User = get_user_model()


class Group(models.Model):
    """Model for a group object.

    Properties:
    title -- a name of a group.
    slug -- a group address, a part of URL. Has to be unique.
    description -- group info.
    """
    title = models.CharField(
        verbose_name='Имя группы',
        max_length=200,
        help_text='Задайте имя вашей группы.',
    )
    slug = models.SlugField(
        verbose_name='Адрес страницы с постами группы.',
        max_length=100,
        unique=True,
        blank=True,
        help_text=(
            'Укажите адрес для страницы группы. Используйте только '
            'латиницу, цифры, дефисы и знаки подчёркивания.'
        ),
    )
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Введите краткое описание вашей группы.',
    )

    class Meta:
        db_table = 'Groups'
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    """Model for a post object.

    Properties:
    text -- post text.
    pub_date -- publication date.
    author -- name of author.
    group -- name of group where post is published.
    """
    text = models.TextField(
        verbose_name='Текст публикации',
        help_text=(
            'Введите текст публикации. '
            'Текст не должен быть пустым или состоять только из пробелов.'
        ),
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        on_delete=models.CASCADE,
        related_name='posts',
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        help_text=('Выберите группу, в которой пост будет опубликован '
                   'или оставьте поле пустым.')
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='posts/',
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'Posts'
        ordering = ('-pub_date',)
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        text = wrap_text(self.text)
        return (
            f'Автор: {self.author}\n'
            f'Группа: {self.group}\n'
            f'Дата публикации: {self.pub_date.strftime("%d.%m.%Y")}\n'
            f'Текст:\n'
            f'{text}\n'
            f'\n'
        )


class Comment(models.Model):
    """Модель для комментариев.
    post - публикация, к которой комментарий относится
    author - автор комментария
    text - текст комментария
    created - дата публикации комментария
    """
    post = models.ForeignKey(
        Post,
        verbose_name='Запись',
        related_name='comments',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='comments',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name='Текст комментария.',
        help_text='Добавьте комментарий.',
    )
    created = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        db_table = 'Comments'
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        text = wrap_text(self.text)
        return (
            f'Автор: {self.author}\n'
            f'Дата: {self.created.strftime("%d.%m.%Y")}\n'
            f'Текст:\n'
            f'{text}\n'
            f'\n'
        )


class FollowQuerySet(models.QuerySet):
    def authors(self):
        return {follow.author for follow in self}


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='following',
        on_delete=models.CASCADE,
    )

    objects = FollowQuerySet.as_manager()

    class Meta:
        db_table = 'Follows'
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('user', 'author')

    def __str__(self):
        return (f'Автор: {self.author}\n'
                f'Подписчик: {self.user}\n')

    def save(self, *args, **kwargs) -> Optional:
        if self.author != self.user:
            return super().save(*args, **kwargs)
        return None
