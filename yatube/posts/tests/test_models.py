from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Comment, Follow, Group, Post

User = get_user_model()


class PostsModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='user1')
        cls.user2 = User.objects.create_user(username='user2')
        cls.group = Group.objects.create(title='Тестовая группа')
        cls.post = Post.objects.create(
            text='Тестовый пост Тестовый пост Тест',
            image='small.gif',
            author=cls.user1,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            text='Текстовый комментарий',
            post=cls.post,
            author=cls.user1,
        )
        cls.follow = Follow.objects.create(
            user=cls.user2,
            author=cls.user1,
        )

    def test_models_str_text(self):
        """Проверка __str__ в моделях приложения posts."""

        list_keys_values = {
            str(self.post): self.post.text[:15],
            str(self.group): self.group.title,
            str(self.comment): self.comment.text[:15],
            str(self.follow): (
                f'{self.follow.user.username} '
                f'подписан на '
                f'{self.follow.author.username}'
            ),
        }

        for key, value in list_keys_values.items():
            with self.subTest(key=key):
                self.assertEqual(key, value, 'Ошибка в названии')

    def test_post_models_verbose_name(self):
        """Проверка, совпадают ли verbose_name, help_text в полях Post."""

        list_post_keys_values = {
            'text': ('Текст статьи', 'Введите текст статьи'),
            'pub_date': ('Дата публикации', 'Укажите дату публикации'),
            'author': ('Автор статьи', 'Укажите автора статьи'),
            'group': (
                'Группа статей',
                'Выберите тематическую группу в выпадающем списке по желанию'),
            'image': ('Картинка статьи', 'Добавьте картинку статьи'),
        }
        for key, value in list_post_keys_values.items():
            with self.subTest(key=key):
                self.assertEqual(
                    self.post._meta.get_field(key).verbose_name, value[0],
                )

        for key, value in list_post_keys_values.items():
            with self.subTest(key=key):
                self.assertEqual(
                    self.post._meta.get_field(key).help_text, value[1],
                )

    def test_group_models_verbose_name(self):
        """Проверка, совпадают ли verbose_name, help_text в полях Group."""

        list_group_keys_values = {
            'title': (
                'Название группы',
                'Введите название тематической группы'
            ),
            'description': (
                'Описание группы',
                'Добавьте текст описания группы'
            ),
        }

        for key, value in list_group_keys_values.items():
            with self.subTest(key=key):
                self.assertEqual(
                    self.group._meta.get_field(key).verbose_name, value[0],
                )

        for key, value in list_group_keys_values.items():
            with self.subTest(key=key):
                self.assertEqual(
                    self.group._meta.get_field(key).help_text, value[1],
                )

    def test_comment_models_verbose_name(self):
        """Проверка, совпадают ли verbose_name в полях Comment."""

        list_comment_keys_values = {
            'post': 'Имя поста',
            'author': 'Имя автора',
            'text': 'Текст комментария',
            'created': 'Дата комментария',
        }

        for key, value in list_comment_keys_values.items():
            with self.subTest(key=key):
                self.assertEqual(
                    self.comment._meta.get_field(key).verbose_name, value,
                )

    def test_follow_models_verbose_name(self):
        """Проверка, совпадают ли verbose_name, help_text в полях Follow."""

        list_follow_keys_values = {
            'user': ('Укажите подписчика', 'Подписчик'),
            'author': ('Укажите на кого подписываемся', 'Автор поста'),
        }

        for key, value in list_follow_keys_values.items():
            with self.subTest(key=key):
                self.assertEqual(
                    self.follow._meta.get_field(key).verbose_name, value[0],
                )

        for key, value in list_follow_keys_values.items():
            with self.subTest(key=key):
                self.assertEqual(
                    self.follow._meta.get_field(key).help_text, value[1],
                )
