from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from http import HTTPStatus


User = get_user_model()

USERS_PAGES_DICT_GUEST = {
    reverse('users:signup'): 'users/signup.html',
    reverse('users:login'): 'users/login.html',
    reverse('users:password_reset'): 'users/password_reset_form.html',
    reverse('users:password_reset_done'): 'users/password_reset_done.html',
    reverse('users:password_reset_confirm', kwargs={
        'uidb64': '16',
        'token': '82e0bc9980a6b2c9a70969b0f8dc974418dda399'
    }):
        'users/password_reset_confirm.html',
    reverse('users:password_reset_complete'):
        'users/password_reset_complete.html',
}

USERS_PAGES_DICT_AUTH = {
    reverse('users:password_change'): 'users/password_change_form.html',
    reverse('users:password_change_done'): 'users/password_change_done.html',
    reverse('users:logout'): 'users/logged_out.html',
}


class UsersPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self) -> None:
        super().setUp()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for name, template in USERS_PAGES_DICT_GUEST.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
        for name, template in USERS_PAGES_DICT_AUTH.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_signup_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
