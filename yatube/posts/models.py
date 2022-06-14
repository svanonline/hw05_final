from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(unique=True, max_length=250,
                            verbose_name='Тег', null=True, blank=True)
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Пост')
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts')
    group = models.ForeignKey(
        Group, blank=True, null=True, on_delete=models.SET_NULL,
        related_name='posts', verbose_name='Группа')

    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Введите комментарий к посту')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
        blank=True,
        null=True,
        help_text='Укажите пост для комментирования',
        related_name='comments')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор',
        help_text='Ваше имя')
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время создания комментария',
        help_text='Время комментирования генерируется автоматически')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created']


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_subscriber'
            )
        ]
