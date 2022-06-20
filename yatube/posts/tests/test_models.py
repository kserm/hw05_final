from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from posts.models import Group, Post, Comment, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.leo = User.objects.create_user(username='leo')
        cls.follower = Follow.objects.create(user=cls.user,
                                             author=cls.leo)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост с очень длинным и содержательным содержимым',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        expected_post_str = post.text[:15]
        group = PostModelTest.group
        comment = PostModelTest.comment

        self.assertEqual(str(post), expected_post_str)
        self.assertEqual(str(group), 'Тестовая группа')
        self.assertEqual(str(comment), 'Тестовый комментарий')

    def test_post_verbose_name(self):
        """verbose_name в полях модели post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_group_verbose_name(self):
        """verbose_name в полях модели group совпадает с ожидаемым."""
        group = PostModelTest.group
        field_verboses = {
            'title': 'Группа',
            'slug': 'URL',
            'description': 'Описание группы',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_comment_verbose_name(self):
        """verbose_name в полях модели comment совпадает с ожидаемым."""
        comment = PostModelTest.comment
        field_verboses = {
            'post': 'Текст поста',
            'author': 'Автор',
            'text': 'Текст комментария',
            'created': 'Дата комментария',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_follow_verbose_name(self):
        """verbose_name в полях модели follow совпадает с ожидаемым."""
        follower = PostModelTest.follower
        field_verboses = {
            'user': 'Пользователь',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follower._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_group_help_text(self):
        """help_text в полях модели group совпадает с ожидаемым."""
        group = PostModelTest.group
        field_help_texts = {
            'title': 'Группа, к которой будет относиться пост',
            'slug': 'Название группы для URL',
            'description': 'Подробное описание группы',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)

    def test_post_help_text(self):
        """help_text в полях модели post совпадает с ожидаемым."""
        comment = PostModelTest.comment
        field_help_texts = {
            'post': 'Текст нового поста',
            'author': 'Автор поста',
            'text': 'Текст нового комментария',
            'created': 'Дата публикации комментария',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).help_text,
                    expected_value
                )

    def test_comment_help_text(self):
        """help_text в полях модели comment совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Текст нового поста',
            'pub_date': 'Дата публикации поста',
            'author': 'Автор поста',
            'group': 'Группа, к которой относится пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

    def test_follow_help_text(self):
        """help_text в полях модели follow совпадает с ожидаемым."""
        follower = PostModelTest.follower
        field_help_texts = {
            'user': 'Пользователь, который подписывается',
            'author': 'Автор, на которого подписываются',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follower._meta.get_field(field).help_text,
                    expected_value
                )

    def test_validate_slug_field(self):
        """Проверяем, что поле slug должно быть уникальным."""
        with self.assertRaises(IntegrityError):
            Group.objects.create(
                title='Тестовая группа',
                slug=self.group.slug,
                description='Тестовое описание',
            )
