from django.core.cache import cache
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group, Comment
from django.urls import reverse
from http import HTTPStatus


User = get_user_model()


POST_URL_DICT_GUEST = {
    '/': 'posts/index.html',
    '/group/test-slug/': 'posts/group_list.html',
    '/profile/auth/': 'posts/profile.html',
    '/posts/1/': 'posts/post_detail.html',
}

POST_URL_DICT_AUTH = {
    '/create/': 'posts/create_post.html',
    '/posts/1/edit/': 'posts/create_post.html',
    '/posts/1/comment/': 'posts/post_detail.html',
    '/follow/': 'posts/follow.html'
}


class PostsURLTests(TestCase):
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
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )

    def setUp(self) -> None:
        super().setUp()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_url_exists_for_guest(self):
        for address in POST_URL_DICT_GUEST.keys():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.guest_client.get('unexisting_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_exists_for_authorized(self):
        for address in POST_URL_DICT_GUEST.keys():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        for address in POST_URL_DICT_AUTH.keys():
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.authorized_client.get('unexisting_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template_for_guest(self):
        for address, template in POST_URL_DICT_GUEST.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
        response = self.guest_client.get('unexisting_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_uses_correct_template_for_authorized(self):
        for address, template in POST_URL_DICT_GUEST.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
        for address, template in POST_URL_DICT_AUTH.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
        response = self.authorized_client.get('unexisting_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_foreign_author_edit_post_redirect(self):
        foreigner = User.objects.create_user(username='foreigner')
        self.foreign_client = Client()
        self.foreign_client.force_login(foreigner)
        response = self.foreign_client.get('/posts/1/edit/', follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail', kwargs={'post_id': 1}
            )
        )

    def test_url_redirects_for_guest(self):
        urls_redirect_dict = {
            reverse('posts:post_create'): '/auth/login/?next=/create/',
            reverse('posts:post_edit', kwargs={'post_id': 1}):
                '/auth/login/?next=/posts/1/edit/',
            reverse('posts:add_comment', kwargs={'post_id': 1}):
                '/auth/login/?next=/posts/1/comment/',
            reverse('posts:follow_index'):
                '/auth/login/?next=/follow/',
        }
        for address, redirect in urls_redirect_dict.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertRedirects(response, redirect)
