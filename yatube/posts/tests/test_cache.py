from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='test_user')

    def setUp(self) -> None:
        super().setUp()
        self.guest_client = Client()

    def test_cashe(self):
        """Проверка хранения поста в кэше. """
        Post.objects.create(text='test_note', author=self.author)
        request1 = self.guest_client.get('/')
        Post.objects.all().delete()
        request2 = self.guest_client.get('/')
        request1_content = str(request1.content)
        request2_content = str(request2.content)
        self.assertHTMLEqual(request1_content, request2_content)
