from django.test import Client, TestCase
from django.urls import reverse

TECH_PAGE_URL = reverse('about:tech')
ABOUT_PAGE_URL = reverse('about:author')


class AboutTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_access(self):
        client = self.guest_client

        urls = [
            TECH_PAGE_URL,
            ABOUT_PAGE_URL,
        ]

        for url in urls:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_templates(self):
        client = self.guest_client

        urls_templates = {
            TECH_PAGE_URL: 'about/tech.html',
            ABOUT_PAGE_URL: 'about/author.html',
        }

        for url, expected_template in urls_templates.items():
            with self.subTest(url=url):
                response = client.get(url)
                self.assertTemplateUsed(response, expected_template)
