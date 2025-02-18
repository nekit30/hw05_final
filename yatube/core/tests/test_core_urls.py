from http import HTTPStatus

from django.test import Client, TestCase


class CoreUrlsTests(TestCase):
    """Проверка корректной работы страницы 404 и её шаблона."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_404_exists_at_desired_location(self):
        response = self.guest_client.get('page').status_code
        self.assertEqual(response, HTTPStatus.NOT_FOUND, 'Error 404 page')

    def test_404_uses_correct_template(self):
        response = self.guest_client.get('page')
        self.assertTemplateUsed(response, 'core/404.html', 'Error 404 temp.')
