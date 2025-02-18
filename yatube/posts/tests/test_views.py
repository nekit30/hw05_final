from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post

User = get_user_model()


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create(username='user1')
        cls.user2 = User.objects.create(username='user2')
        cls.author = User.objects.create(username='author')
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            text='Привет!',
            group=cls.group,
            author=cls.user1,
        )

        cls.follow = Follow.objects.create(
            user=cls.user2,
            author=cls.user1
        )

        cls.templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/post_create.html': reverse('posts:post_create'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'},
            )
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def posts_check_all_fields(self, post):
        """Метод, проверяющий поля поста."""
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.id, self.post.group.id)

    def test_posts_pages_use_correct_template(self):
        """Проверка, использует ли адрес URL соответствующий шаблон."""
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client1.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_context_index_template(self):
        """
        Проверка, сформирован ли шаблон group_list с
        правильным контекстом.

        Появляется ли пост, при создании на главной странице.
        """
        response = self.authorized_client1.get(reverse('posts:index'))
        self.posts_check_all_fields(response.context['page_obj'][0])
        last_post = response.context['page_obj'][0]
        self.assertEqual(last_post, self.post)

    def test_posts_context_group_list_template(self):
        """
        Проверка, сформирован ли шаблон group_list с
        правильным контекстом.

        Появляется ли пост, при создании на странице его группы.
        """
        response = self.authorized_client1.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug},
            )
        )
        test_group = response.context['group']
        self.posts_check_all_fields(response.context['page_obj'][0])
        test_post = str(response.context['page_obj'][0])
        self.assertEqual(test_group, self.group)
        self.assertEqual(test_post, str(self.post))

    def test_posts_context_post_create_template(self):
        """
        Проверка, сформирован ли шаблон post_create с
        правильным контекстом.
        """
        response = self.authorized_client1.get(reverse('posts:post_create'))

        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_posts_context_post_edit_template(self):
        """
        Проверка, сформирован ли шаблон post_edit с
        правильным контекстом.
        """
        response = self.authorized_client1.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id},
            )
        )

        form_fields = {'text': forms.fields.CharField}

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_context_profile_template(self):
        """
        Проверка, сформирован ли шаблон profile с
        правильным контекстом.
        """
        response = self.authorized_client1.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user1.username},
            )
        )
        profile = {'author': self.post.author}

        for value, expected in profile.items():
            with self.subTest(value=value):
                context = response.context[value]
                self.assertEqual(context, expected)

        self.posts_check_all_fields(response.context['page_obj'][0])
        test_page = response.context['page_obj'][0]
        self.assertEqual(test_page, self.user1.posts.all()[0])

    def test_posts_context_post_detail_template(self):
        """
        Проверка, сформирован ли шаблон post_detail с
        правильным контекстом.
        """
        response = self.authorized_client1.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id},
            )
        )

        profile = {'post': self.post}

        for value, expected in profile.items():
            with self.subTest(value=value):
                context = response.context[value]
                self.assertEqual(context, expected)

    def test_posts_not_from_foreign_group(self):
        """
        Проверка, при указании группы поста, попадает
        ли он в другую группу.
        """
        response = self.authorized_client1.get(reverse('posts:index'))
        self.posts_check_all_fields(response.context['page_obj'][0])
        post = response.context['page_obj'][0]
        group = post.group
        self.assertEqual(group, self.group)

    def test_post_comment_guest_user(self):
        """
        Проверка неавторизированного пользователя
        на редирект при попытке комментирования
        и невозможность комментирования.
        """
        comment_count = Comment.objects.count()
        form_data = {'text': 'Test comment'}
        response_guest = self.guest_client.post(
            reverse('posts:post_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        redirect_page = reverse('login') + '?next=%2Fposts%2F1%2Fcomment%2F'
        self.assertRedirects(
            response_guest,
            redirect_page,
            msg_prefix='Ошибка редиректа неавторизованного пользователя.',
        )
        self.assertEqual(
            Comment.objects.count(),
            comment_count,
            'Ошибка изменённого количества комментариев.',
        )

    def test_post_comment_authorized_user(self):
        """
        Проверка авторизированного пользователя
        на редирект после комментирования,
        возможность комментирования,
        изменяемое количество комментариев и их добавление.
        """
        comment_count = Comment.objects.count()
        form_data = {'text': 'Test comment'}
        response_authorized = self.authorized_client1.post(
            reverse('posts:post_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response_authorized,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
            msg_prefix='Ошибка редиректа.',
        )
        self.assertEqual(
            response_authorized.context.get('comments')[0].text,
            'Test comment',
            'Ошибка нахождения комментария на странице поста.',
        )
        self.assertEqual(
            Comment.objects.count(),
            comment_count + 1,
            'Ошибка изменения количества комментариев.'
        )
        self.assertTrue(
            Comment.objects.filter(
                text='Test comment',
                author=self.user1,
                post_id=self.post.id,
            ).exists(),
            'Ошибка нахождения добавленного комментария.'
        )

    def test_post_profile_follow(self):
        """Проверка, возможно ли подписаться на автора поста."""
        self.authorized_client1.get(
            reverse('posts:profile_follow', kwargs={'username': 'author'})
        )
        self.assertTrue(
            Follow.objects.filter(
                author=self.author,
                user=self.user1,
            ).exists(),
        )

    def test_post_profile_unfollow(self):
        """Проверка, возможно ли отписаться от автора поста."""
        self.authorized_client2.get(
            reverse('posts:profile_unfollow', kwargs={'username': 'author'})
        )
        self.assertFalse(
            Follow.objects.filter(
                author=self.author,
                user=self.user2
            ).exists()
        )

    def test_post_follow_index_follower(self):
        """Проверка, находится ли новый пост в ленте подписчика."""
        response_follower = self.authorized_client2.get(
            reverse('posts:follow_index')
        )
        post_follow = response_follower.context.get('page_obj')[0]
        self.assertEqual(post_follow, self.post)

    def test_post_follow_index_unfollower(self):
        """Проверка находится ли пост в ленте не подписчика."""
        response_unfollower = self.authorized_client1.get(
            reverse('posts:follow_index')
        )
        post_unfollow = response_unfollower.context.get('page_obj')
        self.assertEqual(post_unfollow.object_list.count(), 0)


class PostsPaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='Тестовый пользователь')
        cls.authorized_client1 = Client()
        cls.authorized_client1.force_login(cls.user1)
        for count in range(13):
            cls.post = Post.objects.create(
                text=f'Тестовый текст поста номер {count}',
                author=cls.user1,
            )

    def test_posts_if_first_page_has_ten_records(self):
        """Проверка, содержит ли первая страница 10 записей."""
        response = self.authorized_client1.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page_obj').object_list), 10)

    def test_posts_if_second_page_has_three_records(self):
        """Проверка, содержит ли вторая страница 3 записи."""
        response = self.authorized_client1.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context.get('page_obj').object_list), 3)
