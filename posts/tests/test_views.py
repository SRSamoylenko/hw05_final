import re
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.paginator import Paginator
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post
from posts.tests import constants as _
from yatube.settings import POSTS_PER_PAGE

User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class IndexGroupViewsTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create_user(username=_.TEST_USERNAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.second_user = User.objects.create_user(
            username=_.SECOND_TEST_USERNAME
        )
        self.second_authorized_client = Client()
        self.second_authorized_client.force_login(self.second_user)

        Follow.objects.create(
            author=self.user,
            user=self.second_user,
        )

        self.group = Group.objects.create(
            title=_.TEST_GROUP_TITLE,
            slug=_.TEST_GROUP_SLUG,
        )
        self.second_group = Group.objects.create(
            title=_.SECOND_TEST_GROUP_TITLE,
            slug=_.SECOND_TEST_GROUP_SLUG,
        )

        self.post_values = {
            'text': 'Текст для тестирования.',
            'author_id': self.user.id,
            'group_id': self.group.id,
        }
        self.post = Post.objects.create(image=_.TEST_IMAGE, **self.post_values)

    def test_index_group_pages_item_count(self):
        """Проверяет число объектов на страницах."""
        client = self.authorized_client

        urls_count = {
            _.INDEX_URL: 1,
            _.GROUP_POSTS_URL: 1,
            _.SECOND_GROUP_POSTS_URL: 0,
        }

        for url, count in urls_count.items():
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(len(response.context['page']), count)

    def test_follow_page_item_count(self):
        """Проверяет, отображается ли постна странице подписчика
        и не отображается на страницах других пользователей."""
        client_posts = {
            self.authorized_client: 0,
            self.second_authorized_client: 1,
        }

        for client, count in client_posts.items():
            with self.subTest(client=client):
                cache.clear()
                response = client.get(_.FOLLOW_INDEX_URL)
                self.assertEqual(len(response.context['page']), count)

    def test_index_group_pages_show_correct_context(self):
        """Проверяет страницы с постами сформированы с правильным контекстом.
        """
        client = self.second_authorized_client

        urls = (
            _.INDEX_URL,
            _.GROUP_POSTS_URL,
            _.FOLLOW_INDEX_URL,
        )

        for url in urls:
            with self.subTest(url=url):
                cache.clear()
                response = client.get(url)
                first_object = response.context['page'][0]

                for value, expected in self.post_values.items():
                    with self.subTest(value=value):
                        actual = first_object.__dict__[value]
                        self.assertEqual(actual, expected)
                self.assertTrue(
                    re.fullmatch(_.IMAGE_RE, first_object.image.name)
                )

    def test_cache(self):
        client = self.second_authorized_client

        urls = (
            _.INDEX_URL,
            _.FOLLOW_INDEX_URL,
            _.GROUP_POSTS_URL,
        )

        initial_pages = [client.get(url) for url in urls]
        Post.objects.all().delete()
        cached_pages = [client.get(url) for url in urls]
        cache.clear()
        pages = [client.get(url) for url in urls]

        for idx, url in enumerate(urls):
            with self.subTest(url=url):
                self.assertEqual(
                    initial_pages[idx].content, cached_pages[idx].content
                )
                self.assertNotEqual(
                    initial_pages[idx].content, pages[idx].content
                )


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class NewEditPostViewsTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(username=_.TEST_USERNAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.post_values = {
            'text': 'Текст для тестирования.',
            'author_id': self.user.id,
        }
        self.post = Post.objects.create(**self.post_values)

        self.POST_EDIT_URL = reverse('posts:post_edit', kwargs={
            'username': self.post.author.username,
            'post_id': self.post.id,
        })

        self.URLS = [
            _.NEW_POST_URL,
            self.POST_EDIT_URL,
        ]

    def test_post_new_edit_correct_context(self):
        """
        Проверяет если страница с формой поста
        сформирована с правильным контекстом.
        """
        for url in self.URLS:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                form = response.context['form']
                self.assertIsInstance(form, PostForm)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class ProfilePostViewsTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(
            username=_.TEST_USERNAME
        )
        self.second_user = User.objects.create_user(
            username=_.SECOND_TEST_USERNAME
        )

        self.post_data = {
            'text': 'First post.',
            'author_id': self.user.id,
        }
        self.post = Post.objects.create(image=_.TEST_IMAGE, **self.post_data)

        self.second_post = Post.objects.create(
            text='Second post.',
            author=self.second_user,
        )

        self.guest_client = Client()

        self.POST_PAGE_URL = reverse('posts:post', kwargs={
            'username': _.TEST_USERNAME,
            'post_id': self.post.id,
        })

    def test_profile_correct_context(self):
        """Проверяет правильность контекста на странице профиля."""
        posts = Post.objects.filter(author=self.user)
        paginator = Paginator(posts, POSTS_PER_PAGE)
        page = paginator.get_page(1)

        response = self.guest_client.get(_.USER_PROFILE_URL)

        self.assertEqual(response.context.get('person'), self.user)

        actual_page = response.context.get('page')
        self.assertEqual(len(actual_page.object_list), len(page.object_list))

        for actual, expected in zip(actual_page, page):
            with self.subTest(post=expected):
                self.assertEqual(actual, expected)

        actual_post_data = actual_page[0].__dict__
        for field, data in self.post_data.items():
            with self.subTest(field=field):
                self.assertEqual(actual_post_data[field], data)
        self.assertTrue(
            re.fullmatch(_.IMAGE_RE, actual_post_data['image'].name)
        )

    def test_post_page_correct_context(self):
        """Проверяет правильность контекста на странице отдельного поста."""
        expected_context = {
            'person': self.user,
            'post': self.post,
        }

        response = self.guest_client.get(self.POST_PAGE_URL)

        for field, expected in expected_context.items():
            with self.subTest(field=field):
                actual = response.context.get(field)
                self.assertEqual(actual, expected)

        actual_post_data = response.context.get('post').__dict__
        for field, data in self.post_data.items():
            with self.subTest(field=field):
                self.assertEqual(actual_post_data[field], data)
        self.assertTrue(
            re.fullmatch(_.IMAGE_RE, actual_post_data['image'].name)
        )

        actual_form = response.context.get('form')
        self.assertIsInstance(actual_form, CommentForm)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class PaginatorViewsTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create(
            username=_.TEST_USERNAME,
        )

        self.group = Group.objects.create(
            title=_.TEST_GROUP_TITLE,
            slug=_.TEST_GROUP_SLUG,
        )

        self.posts_content = [{
            'text': f'Текст поста {idx + 1} для тестирования.',
            'author_id': self.user.id,
            'group_id': self.group.id,
        } for idx in range(15)]

        posts = [Post(**post_content) for post_content in self.posts_content]
        Post.objects.bulk_create(posts)
        self.posts_content = reversed(self.posts_content)

        self.guest_client = Client()

    def test_index_group_pages_has_correct_objects_amount(self):
        """Проверяет на страницах index и group количество постов."""
        urls = [
            _.INDEX_URL,
            _.GROUP_POSTS_URL,
        ]

        for url in urls:
            with self.subTest(url=url):
                pages_amount = {
                    url: 10,
                    url + '?page=2': 5,
                }

                for page, expected_amount in pages_amount.items():
                    with self.subTest(page=page):
                        cache.clear()
                        response = self.guest_client.get(page)
                        objects = response.context.get('page').object_list
                        actual_amount = len(objects)
                        self.assertEqual(actual_amount, expected_amount)

    def test_index_group_pages_has_correct_objects_context(self):
        """Проверяет контекст на страницах index и group."""
        urls = [
            _.INDEX_URL,
            _.GROUP_POSTS_URL,
        ]

        for url in urls:
            with self.subTest(url=url):
                for idx, expected_content in enumerate(self.posts_content):
                    cache.clear()
                    page_number = idx // POSTS_PER_PAGE
                    response = self.guest_client.get(
                        url + f'?page={page_number + 1}'
                    )

                    with self.subTest(idx=idx):
                        page = response.context.get('page')
                        obj = page.object_list[idx % POSTS_PER_PAGE]
                        actual_content = obj.__dict__
                        for value, expected in expected_content.items():
                            with self.subTest(value=value):
                                self.assertEqual(
                                    actual_content[value],
                                    expected_content[value],
                                )
