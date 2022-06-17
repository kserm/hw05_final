import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.conf import settings
from posts.forms import PostForm
from posts.models import Post, Group, Comment
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from http import HTTPStatus

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def generate_image(self, name):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name=name,
            content=small_gif,
            content_type='image/gif'
        )
        return uploaded

    def test_create_post(self):
        posts_count = Post.objects.count()
        context = {
            'author': 'auth',
            'text': 'Новый тестовый пост',
            'group': (self.group, 1),
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=context,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': 'auth'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Новый тестовый пост',
                group=1
            ).exists()
        )

    def test_edit_post(self):
        posts_count = Post.objects.count()
        new_group = Group.objects.create(
            title='Новая тестовая группа',
            slug='test-slug-new',
            description='Новое тестовое описание',
        )
        context = {
            'text': 'Новый тестовый пост изменен',
            'group': (self.group, new_group.id)
        }
        post = Post.objects.first()
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': post.id}
            ),
            data=context,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Новый тестовый пост изменен',
                group=new_group.id
            ).exists()
        )

    def test_create_post_with_image(self):
        posts_count = Post.objects.count()
        context = {
            'author': 'auth',
            'text': 'Новый тестовый пост с картинкой',
            'group': (self.group, 1),
            'image': self.generate_image('small.gif')
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=context,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': 'auth'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
            text='Новый тестовый пост с картинкой',
            group=1,
            image='posts/small.gif'
        ).exists())

    def test_edit_post_with_image(self):
        posts_count = Post.objects.count()
        context = {
            'text': 'Новый тестовый пост (добавлена картинка)',
            'group': (self.group, 1),
            'image': self.generate_image('small2.gif')
        }
        post = Post.objects.first()
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': post.id}
            ),
            data=context,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Новый тестовый пост (добавлена картинка)',
                group=1,
                image='posts/small2.gif'
            ).exists()
        )

    def test_create_comment(self):
        comments_count = Comment.objects.count()
        post = Post.objects.first()
        context = {
            'post': post,
            'author': self.user,
            'text': 'Новый тестовый комментарий'
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': post.id}
            ),
            data=context,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': post.id})
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Новый тестовый комментарий',
                post=post
            ).exists()
        )
