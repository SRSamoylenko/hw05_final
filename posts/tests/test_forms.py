import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import CommentForm, PostForm
from posts.models import Group, Post
from posts.tests import constants as _

User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class PostFormTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.user = User.objects.create(
            username=_.TEST_USERNAME,
        )
        self.authorized_client.force_login(self.user)

        self.group = Group.objects.create(
            title=_.TEST_GROUP_TITLE,
            slug=_.TEST_GROUP_SLUG,
        )

    def test_create_post(self):
        """Валидная форма создает новый пост."""
        posts_count = Post.objects.count()

        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст',
            'image': _.TEST_IMAGE,
        }

        response = self.authorized_client.post(
            _.NEW_POST_URL,
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, _.INDEX_URL)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text='Тестовый текст',
                image__regex=_.IMAGE_RE,
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует существующий пост."""
        post = Post.objects.create(
            author=self.user,
            text='Начальный текст',
            image=_.TEST_IMAGE,
        )

        kwargs = {
            'username': _.TEST_USERNAME,
            'post_id': post.id,
        }

        post_edit_url = reverse('posts:post_edit', kwargs=kwargs)
        post_page_url = reverse('posts:post', kwargs=kwargs)

        posts_count = Post.objects.count()

        form_data = {
            'text': 'Измененный текст',
            'image': SimpleUploadedFile(
                name='second_small.gif',
                content=_.TEST_IMAGE_BYTES,
                content_type='image/gif',
            ),
        }

        response = self.authorized_client.post(
            post_edit_url,
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, post_page_url)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Измененный текст',
                image__regex=r'second_small.*\.gif',
            ).exists()
        )

    def test_fields(self):
        form = PostForm()

        for field, expected in _.POST_FORM_FIELDS.items():
            with self.subTest(field=field):
                self.assertIsInstance(form.fields[field], expected)


class CommentFormTest(TestCase):
    def setUp(self):
        self.authorized_client = Client()
        self.user = User.objects.create(
            username=_.TEST_USERNAME,
        )
        self.authorized_client.force_login(self.user)

        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
        )

        kwargs = {
            'username': self.user.username,
            'post_id': self.post.id,
        }
        self.POST_PAGE_URL = reverse('posts:post', kwargs=kwargs)
        self.ADD_COMMENT_URL = reverse('posts:add_comment', kwargs=kwargs)

    def test_add_comment(self):
        """Валидная форма добавляет комментарий."""
        post_count = self.post.comments.count()

        form_data = {
            'text': 'Some text.',
        }
        response = self.authorized_client.post(
            self.ADD_COMMENT_URL,
            data=form_data,
            follow=True,
        )

        self.assertRedirects(response, self.POST_PAGE_URL)
        self.assertEqual(self.post.comments.count(), post_count + 1)
        self.assertTrue(
            self.post.comments.filter(
                text='Some text.',
            ).exists()
        )

    def test_fields(self):
        form = CommentForm()

        for field, expected in _.COMMENT_FORM_FIELDS.items():
            with self.subTest(field=field):
                self.assertIsInstance(form.fields[field], expected)
