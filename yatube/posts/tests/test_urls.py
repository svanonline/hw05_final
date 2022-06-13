from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    """Создание тестового поста и группы."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo')
        cls.group = Group.objects.create(
            title='Best group',
            slug='slug',
            description='About group'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Новый пост'
        )

        cls.authorized_client = Client()
        cls.authorized_client.force_login(PostURLTests.user)

    def test_urls_guest(self):
        """Проверяем страницы для гостя."""
        urls = {
            '': HTTPStatus.OK,
            f'/group/{PostURLTests.group.slug}/': HTTPStatus.OK,
            f'/profile/{PostURLTests.user.username}/': HTTPStatus.OK,
            f'/posts/{PostURLTests.post.pk}/': HTTPStatus.OK,
            f'/posts/{PostURLTests.post.pk}/edit/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.FOUND,
        }

        for url, status_code in urls.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_auth(self):
        """Проверяем страницы для авторизованного пользователя."""
        url_status = {
            f'/posts/{PostURLTests.post.pk}/edit/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
        }
        for url, status_code in url_status.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_uses_correct_template(self):
        """Проверяем использование правильных шаблонов."""
        templates_pages_names = [
            ['', 'posts/index.html'],
            [f'/group/{PostURLTests.group.slug}/', 'posts/group_list.html'],
            [f'/profile/{PostURLTests.user.username}/', 'posts/profile.html'],
            [f'/posts/{PostURLTests.post.pk}/', 'posts/post_detail.html'],
            [f'/posts/{PostURLTests.post.pk}/edit/', 'posts/create_post.html'],
            ['/create/', 'posts/create_post.html'],
        ]
        for url, template, in templates_pages_names:
            with self.subTest(url=url):
                self.assertTemplateUsed(self.authorized_client.get(url),
                                        template)
