import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.author = User.objects.create(username='Test')
        cls.group = Group.objects.create(
            title='Test title',
            slug='test-slug',
            description='Test description',
        )
        cls.post = Post.objects.create(
            group=cls.group,
            text='Test text',
            author=cls.author,
        )
        cls.form = PostForm()
        cls.small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                         b'\x01\x00\x80\x00\x00\x00\x00\x00'
                         b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                         b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                         b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                         b'\x0A\x00\x3B')
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif',
        )
        cls.post_new = Post.objects.create(
            text='Test text2',
            group=cls.group,
            author=cls.author,
            image=cls.uploaded,
        )

    def setUp(self) -> None:
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_forms_post_create(self):
        """
        Проверка переадресации, после создания нового поста,
        увеличения количества постов и наличия созданного поста.
        """
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'New post text',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'Test'}),
            msg_prefix='Ошибка переадресации после создания нового поста.'
        )
        self.assertEqual(
            Post.objects.count(),
            post_count + 1,
            'Ошибка количства постов после создания нового поста.'
        )
        self.assertTrue(
            Post.objects.filter(text='New post text').exists(),
            'Ошибка нахождения поста с текстом новой записи.'
        )

    def test_forms_post_edit(self):
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'New post text',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
            msg_prefix='Ошибка работы редиректа.'
        )
        self.assertEqual(
            Post.objects.count(),
            post_count,
            'Ошибка изменения количества постов после редактирования поста.'
        )
        self.assertTrue(
            Post.objects.filter(text='New post text').exists(),
            'Ошибка отсутствия изменения текста редактируемого поста.'
        )

    def test_forms_post_context_has_image(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post_new.id}),
            follow=True
        )
        post_image = response.context.get('post').image
        responses = (
            self.authorized_client.get(
                reverse('posts:group_list', kwargs={'slug': self.group.slug}),
                follow=True
            ),
            self.authorized_client.get(
                reverse('posts:profile', kwargs={'username': 'Test'})
            ),
        )
        for response in responses:
            with self.subTest(response=response):
                self.assertEqual(
                    response.context.get('page_obj')[0].image,
                    'posts/small.gif',
                    'Ошибка нахождения изображения страницы профиля, группы.'
                )
        self.assertEqual(
            post_image,
            'posts/small.gif',
            'Ошибка нахождения изображения на странице поста.'
        )

    def test_forms_post_create_has_image(self):
        """
        Проверка редиректа, при создании поста с изображением,
        нахождения поста с изображением на главной странице,
        увеличенного количества постов на один.
        """
        post_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small2.gif',
            content=self.small_gif,
            content_type='image/gif',
        )
        form_data = {
            'group': self.group.id,
            'text': 'New post text',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'Test'}),
            msg_prefix='Ошибка редиректа при создании поста с изображением.'
        )
        self.assertEqual(
            response.context.get('page_obj')[0].image,
            'posts/small2.gif',
            'Ошибка нахождения изображения на главной странице.'
        )
        self.assertEqual(
            Post.objects.count(),
            post_count + 1,
            'Ошибка количества постов, после добавления поста с изображением.'
        )
