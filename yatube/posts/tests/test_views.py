import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from posts.models import Post, Group, Comment, Follow
from django import forms
from http import HTTPStatus


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
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

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user2 = User.objects.create_user(username='auth2')
        cls.leo = User.objects.create_user(username='leo')
        Follow.objects.create(
            user=cls.user2,
            author=cls.leo
        )
        cls.group1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug1',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug2',
            description='Тестовое описание',
        )
        Post.objects.bulk_create([Post(
            author=cls.user,
            text=f'Тестовый пост {i}',
            group=cls.group1,
            image=cls.generate_image(cls, f'small{i}.gif')
        ) for i in range(1, 11)])
        Post.objects.bulk_create([Post(
            author=cls.user,
            text=f'Тестовый пост {i}',
            group=cls.group2,
            image=cls.generate_image(cls, f'small{i}.gif')
        ) for i in range(11, 16)])
        cls.post = Post.objects.get(id=15)
        Comment.objects.bulk_create([Comment(
            post=cls.post,
            author=cls.user,
            text=f'Тестовый комментарий {i}'
        ) for i in range(1, 11)]
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        super().setUp()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        cache.clear()

    def post_check(self, context):
        for post in context:
            self.assertIsInstance(post, Post)
            self.assertIsNotNone(post.text)
            self.assertIsNotNone(post.group)
            self.assertIsNotNone(post.image)
            self.assertEqual(post.image, f'posts/small{post.pk}.gif')

    def test_posts_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        first_post_id = Post.objects.get(id=1).id
        posts_pages_dict = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group1.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': first_post_id}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': first_post_id}):
                'posts/create_post.html',
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
        }
        for name, template in posts_pages_dict.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(name, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_index_page_1_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом и содержит нужное
        количество постов."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.post_check(response.context['page_obj'])
        posts_count = len(response.context['page_obj'])
        self.assertEqual(posts_count, settings.POSTS_NUM)

    def test_index_page_2_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом и содержит
         нужное количество постов (стр.2)."""
        response = self.authorized_client.get(reverse('posts:index')
                                              + '?page=2')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.post_check(response.context['page_obj'])
        posts_count = len(response.context['page_obj'])
        self.assertEqual(posts_count, 5)

    def test_group_page_1_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом и содержит
         нужное количество постов."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group1.slug}
        ))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.post_check(response.context['page_obj'])
        for post in response.context['page_obj']:
            self.assertEqual(post.group.title, self.group1.title)
            self.assertNotEqual(post.group.title, self.group2.title)
        self.assertIsInstance(response.context['group'], Group)
        posts_count = len(response.context['page_obj'])
        self.assertEqual(posts_count, settings.POSTS_NUM)

    def test_group_page_2_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом и содержит
         нужное количество постов (стр.2)."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group2.slug}
        ))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.post_check(response.context['page_obj'])
        for post in response.context['page_obj']:
            self.assertEqual(post.group.title, self.group2.title)
            self.assertNotEqual(post.group.title, self.group1.title)
        self.assertIsInstance(response.context['group'], Group)
        posts_count = len(response.context['page_obj'])
        self.assertEqual(posts_count, 5)
        diff_group_posts = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group1.slug}
        ))
        self.assertNotEqual(diff_group_posts.context['group'].title,
                            response.context['group'].title)

    def test_profile_page_1_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом и содержит
         нужное количество постов."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}
        ))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.post_check(response.context['page_obj'])
        self.assertIsInstance(response.context['author'],
                              User)
        posts_count = len(response.context['page_obj'])
        self.assertEqual(posts_count, settings.POSTS_NUM)

    def test_profile_page_2_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом и содержит
         нужное количество постов (стр.2)."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}
        ) + '?page=2')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.post_check(response.context['page_obj'])
        self.assertIsInstance(response.context['author'],
                              User)
        posts_count = len(response.context['page_obj'])
        self.assertEqual(posts_count, 5)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}
        ))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post_resp = response.context['post']
        post_obj = Post.objects.get(pk=self.post.id)
        self.assertIsInstance(post_resp, Post)
        self.assertEqual(post_resp.id, post_obj.id)
        self.assertEqual(post_resp.text, post_obj.text)
        self.assertEqual(post_resp.group, post_obj.group)
        self.assertEqual(post_resp.image, post_obj.image)
        self.assertEqual(post_resp.image, f'posts/small{self.post.id}.gif')
        comments_resp = response.context['comments']
        comments_obj = Comment.objects.filter(post=post_obj)
        for i in range(len(comments_resp)):
            self.assertIsInstance(comments_resp[i], Comment)
            self.assertEqual(comments_resp[i].id, comments_obj[i].id)
            self.assertEqual(comments_resp[i].text, comments_obj[i].text)
            self.assertEqual(comments_resp[i].post, post_obj)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_add_comment_page_show_correct_context(self):
        """Шаблон add_comment сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.id}),
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_not_available_for_guest(self):
        """Шаблон post_create недоступен для неавторизованного пользователя"""
        response = self.guest_client.get(reverse('posts:post_create'))
        self.assertTemplateNotUsed(response, 'posts/create_post.html')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_add_comment_page_not_available_for_guest(self):
        """Шаблон add_comment недоступен для неавторизованного пользователя"""
        response = self.guest_client.get(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}))
        self.assertTemplateNotUsed(response, 'posts/post_detail.html')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': Post.objects.get(id=1).id}
        ))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_not_available_for_guest(self):
        """Шаблон post_edit недоступен для неавторизованного пользователя"""
        response = self.guest_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': Post.objects.get(id=1).id}
        ))
        self.assertTemplateNotUsed(response, 'posts/create_post.html')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_cached_index_content(self):
        """Проверка, что при удалении записи из базы, она остаётся в response
        content главной страницы до принудительной очистки"""
        cached_post = Post.objects.create(
            author=self.user,
            group=self.group1,
            text='Тщательно закэшированный пост'
        )
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(bytes(cached_post.text, encoding='utf-8'),
                      response.content)
        cached_post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn(bytes(cached_post.text, encoding='utf-8'),
                      response.content)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotIn(bytes(cached_post.text, encoding='utf-8'),
                         response.content)

    def test_authorized_can_follow(self):
        """Проверка, что авторизованный пользователь может подписываться
        на других пользователей"""
        self.authorized_client.get(f'/profile/{self.leo}/follow/')
        self.assertTrue(Follow.objects.filter(
            user=self.user,
            author=self.leo
        ).exists())

    def test_authorized_can_unfollow(self):
        """Проверка, что авторизованный пользователь может отписываться
        на других пользователей"""
        self.authorized_client2.get(f'/profile/{self.leo}/unfollow/')
        self.assertFalse(Follow.objects.filter(
            user=self.user2,
            author=self.leo
        ).exists())

    def test_new_post_available_for_follower(self):
        """Проверка, что новая запись пользователя появляется в ленте тех,
        кто на него подписан"""
        new_post = Post.objects.create(
            text='Новый пост Львяша',
            author=self.leo,
        )
        response = self.authorized_client2.get(reverse('posts:follow_index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(new_post, response.context['page_obj'])

    def test_new_post_not_available_for_non_follower(self):
        """Проверка, что новая запись пользователя не появляется в ленте тех,
        кто не подписан"""
        new_post = Post.objects.create(
            text='Еще один новый пост Львяша',
            author=self.leo,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn(new_post, response.context['page_obj'])
