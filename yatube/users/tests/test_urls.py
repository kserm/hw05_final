from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model


User = get_user_model()

USERS_URL_DICT_GUEST = {
    '/auth/signup/': 'users/signup.html',
    '/auth/login/': 'users/login.html',
    '/auth/password_reset/': 'users/password_reset_form.html',
    '/auth/password_reset/done/': 'users/password_reset_done.html',
    '/auth/reset/<uidb64>/<token>/': 'users/password_reset_confirm.html',
    '/auth/reset/done': 'users/password_reset_complete.html',
}

USERS_URL_DICT_AUTH = {
    '/auth/password_change/': 'users/password_change_form.html',
    '/auth/password_change/done/': 'users/password_change_done.html',
    '/auth/logout/': 'users/logged_out.html',
}


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self) -> None:
        super().setUp()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_exists_for_guest(self):
        for address in USERS_URL_DICT_GUEST.keys():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_for_authorized(self):
        for address in USERS_URL_DICT_GUEST.keys():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        for address in USERS_URL_DICT_AUTH.keys():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template_for_guest(self):
        for address, template in USERS_URL_DICT_GUEST.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_for_authorized(self):
        for address, template in USERS_URL_DICT_GUEST.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
        for address, template in USERS_URL_DICT_AUTH.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
