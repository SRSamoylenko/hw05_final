from django.test import TestCase

from posts.models import Comment, Follow, Group, Post, User
from posts.tests import constants as _
from yatube.utils import wrap_text


class PostModelTest(TestCase):
    def test_fields(self):  # noqa
        """Проверяет правильность настроек полей."""    # noqa
        for field, expected_values in _.POST_MODEL_FIELDS.items():
            with self.subTest(field=field):
                for option, expected_value in expected_values.items():
                    with self.subTest(option=option):
                        self.assertEqual(
                            Post._meta.get_field(field).__dict__[option],
                            expected_value
                        )

    def test_object_name(self):
        """Проверяет правильность вывода метода __str__."""
        user = User.objects.create(
            username=_.TEST_USERNAME,
        )
        post = Post.objects.create(
            text='Тестовый текст.',
            author=user,
        )
        text = wrap_text(post.text)
        expected_output = _.POST_STR_OUTPUT.format(
            author=post.author,
            group=post.group,
            pub_date=post.pub_date.strftime('%d.%m.%Y'),
            text=text,
        )
        self.assertEquals(expected_output, str(post))


class GroupModelTest(TestCase):
    def test_fields(self):  # noqa
        """Проверяет правильность настроек полей."""    # noqa
        for field, expected_values in _.GROUP_MODEL_FIELDS.items():
            with self.subTest(field=field):
                for option, expected_value in expected_values.items():
                    with self.subTest(option=option):
                        self.assertEqual(
                            Group._meta.get_field(field).__dict__[option],
                            expected_value
                        )

    def test_object_name(self):
        """Проверяет правильность вывода метода __str__."""
        group = Group.objects.create(
            title='Тестовая группа',
        )
        expected_output = _.GROUP_STR_OUTPUT.format(title=group.title)
        self.assertEquals(str(group), expected_output)


class CommentModelTest(TestCase):
    def test_fields(self):  # noqa
        """Проверяет правильность настроек полей."""    # noqa
        for field, expected_values in _.COMMENT_MODEL_FIELDS.items():
            with self.subTest(field=field):
                for option, expected_value in expected_values.items():
                    with self.subTest(option=option):
                        self.assertEqual(
                            Comment._meta.get_field(field).__dict__[option],
                            expected_value
                        )

    def test_object_name(self):
        """Проверяет правильность вывода метода __str__."""
        author = User.objects.create(username=_.TEST_USERNAME)
        post = Post.objects.create(author=author, text='.')
        comment = Comment.objects.create(
            post=post,
            author=author,
            text='Текст.',
        )
        text = wrap_text(comment.text)

        expected_output = _.COMMENT_STR_OUTPUT.format(
            author=comment.author,
            created=comment.created.strftime('%d.%m.%Y'),
            text=text,
        )
        self.assertEquals(str(comment), expected_output)


class FollowModelTest(TestCase):
    def test_fields(self):  # noqa
        """Проверяет правильность настроек полей."""    # noqa
        for field, expected_values in _.FOLLOW_MODEL_FIELDS.items():
            with self.subTest(field=field):
                for option, expected_value in expected_values.items():
                    with self.subTest(option=option):
                        self.assertEqual(
                            Follow._meta.get_field(field).__dict__[option],
                            expected_value
                        )
