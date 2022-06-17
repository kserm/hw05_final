from django.contrib.auth import get_user_model
from users.forms import CreationForm
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus

User = get_user_model()


class UsersCreationFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(
            first_name='Author',
            last_name='Authorov',
            username='auth',
            email='author@mail.com',
        )
        cls.form = CreationForm()

    def setUp(self) -> None:
        super().setUp()
        self.guest_client = Client()

    def test_user_signup(self):
        users_count = User.objects.count()
        context = {
            'first_name': 'Лев',
            'last_name': 'Толстой',
            'username': 'leo',
            'email': 'leo@example.com',
            'password1': 'drobnbobn11',
            'password2': 'drobnbobn11'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=context,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:index')
        )
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name='Лев',
                last_name='Толстой',
                username='leo',
                email='leo@example.com'
            ).exists()
        )

    def test_cant_create_existing_user(self):
        users_count = User.objects.count()
        context = {
            'username': 'auth',
            'password1': 'drobnbobn11',
            'password2': 'drobnbobn11'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=context,
            follow=True,
        )
        self.assertEqual(User.objects.count(), users_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
