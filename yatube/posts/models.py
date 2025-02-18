from django.contrib.auth.models import User
from django.db import models


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст статьи',
        help_text='Введите текст статьи',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Укажите дату публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор статьи',
        help_text='Укажите автора статьи',
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа статей',
        help_text='Выберите тематическую группу '
                  'в выпадающем списке по желанию',
    )
    image = models.ImageField(
        verbose_name='Картинка статьи',
        help_text='Добавьте картинку статьи',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
        help_text='Введите название тематической группы',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Номер группы',
        help_text='Укажите порядковый номер группы',
    )
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Добавьте текст описания группы',
    )

    class Meta:
        verbose_name = 'Группа статей'
        verbose_name_plural = 'Группы статей'
        ordering = ('-title',)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Имя поста',
        help_text='Укажите имя поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Имя автора',
        help_text='Укажите автора',
    )
    text = models.TextField(
        max_length=300,
        verbose_name='Текст комментария',
        help_text='Укажите текст комментария',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария',
        help_text='Укажите дату комментария',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-created',)

    def __str__(self) -> str:
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Укажите подписчика',
        help_text='Подписчик',
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Укажите на кого подписываемся',
        help_text='Автор поста',
    )

    class Meta:
        ordering = ('-user',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follows',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user.username} подписан на {self.author.username}'
