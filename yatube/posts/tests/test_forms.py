import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create(username='TestUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            slug='test-slug',
            title='TestGroup',
            description='test-desc'
        )
        cls.post = Post.objects.create(
            text='TestPost',
            author=cls.user,
            group=cls.group,
            image='posts/small.gif',
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post(self):
        """ Проверка создания поста """
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
            content_type='image/gif',

        )
        count_before = Post.objects.count()
        form_data = {
            'text': PostFormTest.post.text,
            'image': uploaded,
            'group': PostFormTest.group.pk
        }

        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertEqual(count_before + 1, Post.objects.count(), (
            ' Пост не был создан '
        ))

        # Посты отсортированы от самых новых
        new_post = Post.objects.order_by('-id')[0]
        self.assertEqual(new_post.text, form_data['text'], (
            ' Текст нового поста не соответствует введенным данным '
        ))
        self.assertEqual(new_post.group.pk, form_data['group'], (
            ' Группа нового поста не соответствует введеным данным'
        ))
        self.assertEqual(new_post.image, self.post.image)

    def test_edit_post(self):
        form_data = {
            'text': 'Измененный старый пост',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ),
            data=form_data,

        )
        post = Post.objects.get(pk=self.post.pk)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}
        ))
        self.assertEqual(
            post.text,
            form_data['text']
        )
        self.assertEqual(
            post.group.pk,
            form_data['group']
        )

    def test_authorized_user_can_comment(self):
        """ Только авторизованный пользователь может комментировать """
        form_data = {
            'text': 'Test-text',
        }

        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={
                    'post_id': self.post.id
                }),
            data=form_data,
            follow=True
        )
        new_comment = response.context['comments']
        count_before = len(new_comment)
        self.assertEqual(new_comment[0].text, form_data['text'], (
            ' Комментарий авторизованного пользователя не создан '
        ))

        response = self.client.post(
            reverse(
                'posts:add_comment',
                kwargs={
                    'post_id': self.post.id
                }),
            data=form_data,
            follow=True
        )

        self.assertEqual(count_before, self.post.comments.count(), (
            ' Неавторизованный пользователь добавил комментарий '
        ))
