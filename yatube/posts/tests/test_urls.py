from django.core.cache import cache
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group, Comment
from django.urls import reverse
from http import HTTPStatus


User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.foreigner = User.objects.create_user(username='foreigner')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )
        cls.post_url_dict_guest = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
        }
        cls.post_url_dict_auth = {
            '/create/': 'posts/create_post.html',
            f'/posts/{cls.post.id}/edit/': 'posts/create_post.html',
            f'/posts/{cls.post.id}/comment/': 'posts/post_detail.html',
            '/follow/': 'posts/follow.html'
        }

    def setUp(self) -> None:
        super().setUp()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.foreign_client = Client()
        self.foreign_client.force_login(self.foreigner)
        cache.clear()

    def test_url_exists_for_guest(self):
        for address in self.post_url_dict_guest.keys():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.guest_client.get('unexisting_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_exists_for_authorized(self):
        for address in self.post_url_dict_guest.keys():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        for address in self.post_url_dict_auth.keys():
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.authorized_client.get('unexisting_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template_for_guest(self):
        for address, template in self.post_url_dict_guest.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
        response = self.guest_client.get('unexisting_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_uses_correct_template_for_authorized(self):
        for address, template in self.post_url_dict_guest.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
        for address, template in self.post_url_dict_auth.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
        response = self.authorized_client.get('unexisting_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_foreign_author_edit_post_redirect(self):
        response = self.foreign_client.get(f'/posts/{self.post.id}/edit/',
                                           follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            )
        )

    def test_url_redirects_for_guest(self):
        urls_redirect_dict = {
            reverse('posts:post_create'): '/auth/login/?next=/create/',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                f'/auth/login/?next=/posts/{self.post.id}/edit/',
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}):
                f'/auth/login/?next=/posts/{self.post.id}/comment/',
            reverse('posts:follow_index'):
                '/auth/login/?next=/follow/',
        }
        for address, redirect in urls_redirect_dict.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertRedirects(response, redirect)
