from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

TEST_USERNAME = 'test_username'
SECOND_TEST_USERNAME = 'second_test_username'
TEST_GROUP_TITLE = 'test group'
TEST_GROUP_SLUG = 'test-group'
SECOND_TEST_GROUP_TITLE = 'test group 2'
SECOND_TEST_GROUP_SLUG = 'test-group-2'
TEST_IMAGE_BYTES = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00'
    b'\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
    b'\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)
IMAGE_RE = r'posts/small.*\.gif'
TEST_IMAGE = SimpleUploadedFile(
    name='small.gif',
    content=TEST_IMAGE_BYTES,
    content_type='image/gif',
)

INDEX_URL = reverse('posts:index')
FOLLOW_INDEX_URL = reverse('posts:follow_index')
NEW_POST_URL = reverse('posts:new_post')
GROUP_POSTS_URL = reverse('posts:group', kwargs={
    'slug': TEST_GROUP_SLUG,
})
SECOND_GROUP_POSTS_URL = reverse('posts:group', kwargs={
    'slug': SECOND_TEST_GROUP_SLUG,
})
USER_PROFILE_URL = reverse('posts:profile', kwargs={
    'username': TEST_USERNAME,
})
SECOND_USER_PROFILE_URL = reverse('posts:profile', kwargs={
    'username': SECOND_TEST_USERNAME,
})
USER_FOLLOW_URL = reverse('posts:profile_follow', kwargs={
    'username': TEST_USERNAME,
})
USER_UNFOLLOW_URL = reverse('posts:profile_unfollow', kwargs={
    'username': TEST_USERNAME,
})
LOGIN_URL = reverse('login')
ERROR_404_URL = reverse('posts:page_not_found')
ERROR_500_URL = reverse('posts:server_error')

POST_MODEL_FIELDS = {
    'text': {
        'verbose_name': 'Текст публикации',
        'help_text': (
            'Введите текст публикации. '
            'Текст не должен быть пустым '
            'или состоять только из пробелов.'
        ),
    },
    'pub_date': {
        'verbose_name': 'Дата публикации',
        'auto_now_add': True,
    },
    'author': {
        'verbose_name': 'Автор публикации'
    },
    'group': {
        'verbose_name': 'Группа',
        'blank': True,
        'null': True,
        'help_text': (
            'Выберите группу, в которой пост будет опубликован '
            'или оставьте поле пустым.'
        ),
    },
    'image': {
        'verbose_name': 'Изображение',
        'blank': True,
        'null': True,
        'upload_to': 'posts/',
    }
}
POST_STR_OUTPUT = (
    'Автор: {author}\n'
    'Группа: {group}\n'
    'Дата публикации: {pub_date}\n'
    'Текст:\n'
    '{text}\n'
    '\n'
)

GROUP_MODEL_FIELDS = {
    'title': {
        'verbose_name': 'Имя группы',
        'max_length': 200,
        'help_text': 'Задайте имя вашей группы.',
    },
    'slug': {
        'verbose_name': 'Адрес страницы с постами группы.',
        'max_length': 100,
        '_unique': True,
        'blank': True,
        'help_text': (
            'Укажите адрес для страницы группы. Используйте только '
            'латиницу, цифры, дефисы и знаки подчёркивания.'
        ),
    },
    'description': {
        'verbose_name': 'Описание группы',
        'help_text': 'Введите краткое описание вашей группы.',
    }
}
GROUP_STR_OUTPUT = '{title}'

COMMENT_MODEL_FIELDS = {
    'post': {
        'verbose_name': 'Запись',
    },
    'author': {
        'verbose_name': 'Пользователь',
    },
    'text': {
        'verbose_name': 'Текст комментария.',
        'help_text': 'Добавьте комментарий.',
    },
    'created': {
        'verbose_name': 'Дата публикации',
        'auto_now_add': True,
    },
}
COMMENT_STR_OUTPUT = (
    'Автор: {author}\n'
    'Дата: {created}\n'
    'Текст:\n'
    '{text}\n'
    '\n'
)

FOLLOW_MODEL_FIELDS = {
    'author': {
        'verbose_name': 'Автор',
    },
    'user': {
        'verbose_name': 'Подписчик',
    }
}
FOLLOW_STR_OUTPUT = (
    'Автор: {author}\n'
    'Подписчик: {user}\n'
)

POST_FORM_FIELDS = {
    'text': forms.fields.CharField,
    'group': forms.fields.ChoiceField,
    'image': forms.fields.ImageField,
}
COMMENT_FORM_FIELDS = {
    'text': forms.fields.CharField,
}
