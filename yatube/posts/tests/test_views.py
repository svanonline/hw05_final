import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post

User = get_user_model()


class TestPaginator(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="TestUser")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        for i in range(15):
            Post.objects.create(
                text=f'{i} note',
                author=cls.user,
                group=cls.group
            )

    def test_index_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj'].object_list),
            settings.POST_LENGTH)

    def test_second_page_contains_5_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(response.context['page_obj'].object_list),
            Post.objects.count() - settings.POST_LENGTH)

    def test_group_page_contains_ten_records(self):
        response = self.client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}))
        self.assertEqual(
            len(response.context['page_obj'].object_list),
            settings.POST_LENGTH)

    def test_profile_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:profile', kwargs={
                                   'username': self.user.username}))
        self.assertEqual(
            len(response.context['page_obj'].object_list),
            settings.POST_LENGTH)


class CommonViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.user = User.objects.create(username='TestUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='test',
            slug='test-slug',
            description='test-desc'
        )
        cls.post = Post.objects.create(
            text=f'Тестовый текст{id,1}',
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/group_list.html': (
                reverse('posts:group_posts', kwargs={
                        'slug': self.group.slug})
            ),
        }

        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        """Index сформрована правильно."""
        response = self.authorized_client.get(reverse('posts:index'))
        index_p = response.context['page_obj'][0]
        self.assertEqual(index_p.id, self.post.id)
        self.assertEqual(index_p.author.id, self.post.author.id)
        self.assertEqual(index_p.group.id, self.post.group.id)

    def test_group_shows_correct_context(self):
        """ Тест шаблона group.html с context """
        response = self.authorized_client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': self.group.slug}
        ))

        self.assertEqual(response.context['group'], self.group, (
            'Тестирование context страницы группы прошло неудачно'
        ))

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_exists_on_main_page(self):
        """ Тест на появление поста на главной страницы после создания """

        response = self.authorized_client.get(reverse('posts:index'))
        count_before = len(response.context['page_obj'])

        created_post = Post.objects.create(
            text='текст',
            author=self.user,
            group=self.group
        )

        response = self.authorized_client.get(reverse('posts:index'))
        count_after = len(response.context['page_obj'])
        new_post = response.context['page_obj'].object_list[0]

        self.assertEqual(count_before + 1, count_after, (
            ' Пост не добавился на главную страницу '
        ))
        self.assertEqual(created_post, new_post, (
            ' Созданный пост не соответствует посту на главной странице '
        ))

    def test_post_exists_on_related_group_page(self):
        """ Тест на появление поста на странице группы после создания """
        response = self.authorized_client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': self.group.slug}
        ))

        test_post = response.context['page_obj'].object_list[0]
        self.assertEqual(self.post, test_post, (
            "Пост не добавился на страницу группы"
        ))

    def test_post_not_belongs_to_alien_group(self):

        alien_group = Group.objects.create(
            title='alien',
            slug='alien-slug',
            description='alien-desc'
        )

        response = self.authorized_client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': alien_group.slug}
        ))

        alien_posts = response.context['page_obj']

        self.assertNotIn(self.post, alien_posts, (
            ' Пост принадлежит чужой группе '
        ))

    def test_profile_shows_correct_context(self):
        """ Тест на корректный context на странице пользователя """
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        ))

        test_author = response.context['author']
        self.assertEqual(test_author, self.user, (
            ' Указан неверный автор '
        ))

        posts = response.context['page_obj']
        self.assertIn(self.post, posts, (
            ' Пост автора не отображается на странице автора '
        ))

    def test_post_view_passes_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.pk}))
        post = response.context.get('post')
        self.assertEqual(post, self.post)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_index_post_with_image_context_correct(self):
        """ Тестирование картинки в context поста на index.html """
        response = self.authorized_client.get(reverse('posts:index'))

        test_image = response.context['page_obj'].object_list[0].image
        self.assertEqual(test_image, self.post.image, (
            ' Картинка поста на главной странице неверно отображается '
        ))

    def test_profile_post_with_image_context_correct(self):
        """ Тестирование картинки в context поста на profile.html """
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))

        test_image = response.context['page_obj'].object_list[0].image
        self.assertEqual(test_image, self.post.image, (
            ' Картинка поста на странице профиля неверно отображается '
        ))

    def test_post_with_image_context_correct(self):
        """ Тестирование картинки в context на отдельном посте """
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={
                'post_id': self.post.id
            }
        ))
        test_image = response.context['post'].image
        self.assertEqual(test_image, self.post.image, (
            ' Картинка поста на странице поста неверно отображается '
        ))

    def test_group_post_with_image_context_correct(self):
        """ Тестирование картинки в context поста на group.html """
        response = self.authorized_client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': self.group.slug}))

        test_image = response.context['page_obj'].object_list[0].image
        self.assertEqual(test_image, self.post.image, (
            ' Картинка поста на странице группы неверно отображается '
        ))

    def test_cache(self):
        """ Тестирование работы кэша"""
        # Делаем запрос до создания поста
        response_before = self.authorized_client.get(reverse('posts:index'))

        # Создаем пост
        post = Post.objects.create(text='test', author=self.user)
        response_after = self.authorized_client.get(reverse('posts:index'))
        Post.objects.filter(id=post.id).delete()

        # Удалили пост из бд, но на странице должен еще быть
        response_after_delete = self.authorized_client.get(
            reverse('posts:index'))
        self.assertEqual(response_after.content, response_after_delete.content)

        # Пост должен быть удален с главной страницы
        cache.clear()
        response_after_clear = self.authorized_client.get(
            reverse('posts:index'))
        # До создания был 1 пост из setUp
        self.assertEqual(
            response_after_clear.context['paginator'].count,
            response_before.context['paginator'].count)

    def test_authorized_user_follow(self):
        """ Тестирование подписки авторизованным пользователем """
        new_user = User.objects.create(username='NewUser')
        new_authorized_client = Client()
        new_authorized_client.force_login(new_user)

        new_authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username}
        ))

        follow_obj = Follow.objects.get(author=self.user, user=new_user)
        self.assertIsNotNone(follow_obj, (
            ' Пользователь не смог подписаться на пользователя '))

    def test_authorized_user_unfollow(self):
        """ Тестирование отписки авторизованным пользователем """
        new_user = User.objects.create(username='NewUser')
        new_authorized_client = Client()
        new_authorized_client.force_login(new_user)

        # Follow (works previous test)
        new_authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username}
        ))

        # Unfollow
        new_authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user.username}
        ))

        self.assertEqual(Follow.objects.count(), 0, (
            'Пользователь не смог отписаться от пользователя'))

    def test_following_posts_showing_to_followers(self):
        """ Тестирование отображения постов отслеживаемых авторов """
        new_user = User.objects.create(username='NewUser')
        new_authorized_client = Client()
        new_authorized_client.force_login(new_user)

        new_authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username}
        ))

        response = new_authorized_client.get(reverse('posts:follow_index'))
        following_post = response.context['page_obj'].object_list[0]
        self.assertEqual(following_post, self.post, (
            'Посты отслеживаемого автора не отображаются на странице избранных'
        ))

        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(response.context['paginator'].count, 0, (
            'Посты неотслеживаемого автора появляются на странице избранных'
        ))
