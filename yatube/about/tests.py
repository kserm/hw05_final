from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus


ABOUT_URLS_DICT = {
    '/about/author/': 'about/author.html',
    '/about/tech/': 'about/tech.html',
}

ABOUT_VIEWS_DICT = {
    'about:author': 'about/author.html',
    'about:tech': 'about/tech.html',
}


class AboutTests(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов /about/..."""
        for address in ABOUT_URLS_DICT.keys():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблона для адреса /about/..."""
        for address, template in ABOUT_URLS_DICT.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_about_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени static_pages:about, доступен."""
        for name in ABOUT_VIEWS_DICT.keys():
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_page_uses_correct_template(self):
        """При запросе к staticpages:about применяется шаблон
        staticpages/about.html."""
        for name, template in ABOUT_VIEWS_DICT.items():
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
