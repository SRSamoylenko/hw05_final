from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post
from posts.tests import constants as _

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title=_.TEST_GROUP_TITLE,
            slug=_.TEST_GROUP_SLUG,
        )

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create_user(
            username=_.TEST_USERNAME,
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.second_user = User.objects.create_user(
            username=_.SECOND_TEST_USERNAME,
        )
        self.second_authorized_client = Client()
        self.second_authorized_client.force_login(self.second_user)

        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый текст.'
        )

        kwargs = {
            'username': _.TEST_USERNAME,
            'post_id': self.post.id,
        }

        self.POST_PAGE_URL = reverse('posts:post', kwargs=kwargs)
        self.POST_EDIT_URL = reverse('posts:post_edit', kwargs=kwargs)
        self.POST_COMMENT_URL = reverse('posts:add_comment', kwargs=kwargs)

    def test_url_names(self):
        """Проверяет, если URL страниц соответствуют ожидаемым."""
        urls = {
            _.INDEX_URL: '/',
            _.FOLLOW_INDEX_URL: '/follow/',
            _.NEW_POST_URL: '/new/',
            _.GROUP_POSTS_URL: f'/group/{_.TEST_GROUP_SLUG}/',
            _.USER_PROFILE_URL: f'/{_.TEST_USERNAME}/',
            _.USER_FOLLOW_URL: f'/{_.TEST_USERNAME}/follow/',
            _.USER_UNFOLLOW_URL: f'/{_.TEST_USERNAME}/unfollow/',
            self.POST_PAGE_URL: f'/{_.TEST_USERNAME}/{self.post.id}/',
            self.POST_EDIT_URL: f'/{_.TEST_USERNAME}/{self.post.id}/edit/',
            self.POST_COMMENT_URL: (f'/{_.TEST_USERNAME}/'
                                    f'{self.post.id}/comment/'),
        }

        for actual, expected in urls.items():
            with self.subTest(url=expected):
                self.assertEqual(actual, expected)

    def test_unauthorized_user_access(self):
        """Проверяет код 200 страниц, доступных неавторизованным пользователям.
        """
        urls = (
            _.INDEX_URL,
            _.GROUP_POSTS_URL,
            _.USER_PROFILE_URL,
            self.POST_PAGE_URL,
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unauthorized_user_redirects(self):
        """Проверяет правильность переадресации неавторизованных пользователей.
        """
        urls = (
            _.FOLLOW_INDEX_URL,
            _.NEW_POST_URL,
            _.USER_FOLLOW_URL,
            _.USER_UNFOLLOW_URL,
            self.POST_EDIT_URL,
            self.POST_COMMENT_URL,
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response, (_.LOGIN_URL + '?next=' + url)
                )

    def test_authorized_user_access(self):
        """Проверяет код 200 страниц, доступных авторизованным пользователям.
        """
        urls = (
            _.NEW_POST_URL,
            _.FOLLOW_INDEX_URL,
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_access(self):
        """Проверяет доступ пользователя к редактированию собственных постов.
        """
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_redirects(self):
        """Проверяет переадресацию со страницы редактирования поста
        для неавторизованных или сторонних пользователей.
        """
        clients = {
            'authorized_client': self.second_authorized_client,
        }

        for client_name, client in clients.items():
            with self.subTest(client=client_name):
                response = client.post(
                    self.POST_EDIT_URL,
                    follow=True
                )
                self.assertRedirects(
                    response,
                    self.POST_PAGE_URL
                )

    def test_comment_post_redirects(self):
        response = self.authorized_client.post(
            self.POST_COMMENT_URL,
            follow=True,
        )
        self.assertRedirects(
            response,
            self.POST_PAGE_URL
        )

    def test_follow_unfollow_urls(self):
        client = self.second_authorized_client
        follow_count = Follow.objects.count()
        author = User.objects.get(username=_.TEST_USERNAME)
        user = self.second_user

        response = client.get(_.USER_FOLLOW_URL, follow=True)
        self.assertRedirects(response, _.USER_PROFILE_URL)
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(Follow.objects.filter(
            author=author,
            user=user,
        ).exists())

        response = client.get(_.USER_UNFOLLOW_URL, follow=True)
        self.assertRedirects(response, _.USER_PROFILE_URL)
        self.assertEqual(Follow.objects.count(), follow_count)
        self.assertFalse(Follow.objects.filter(
            author=author,
            user=user,
        ).exists())

    def test_templates(self):
        """Проверяет правильность выводимых шаблонов."""
        url_templates = {
            _.INDEX_URL: 'index.html',
            _.GROUP_POSTS_URL: 'group.html',
            _.NEW_POST_URL: 'posts/new_post.html',
            self.POST_EDIT_URL: 'posts/new_post.html',
            self.POST_PAGE_URL: 'posts/post.html',
            _.USER_PROFILE_URL: 'posts/profile.html',
        }

        for url, template in url_templates.items():
            with self.subTest(url=url):
                cache.clear()
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)


class ErrorHandlersTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_not_found_handler(self):
        response = self.client.get(_.ERROR_404_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        response = self.client.get('/not-existing-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_server_error(self):
        response = self.client.get(_.ERROR_500_URL)
        self.assertEqual(
            response.status_code,
            HTTPStatus.INTERNAL_SERVER_ERROR
        )
