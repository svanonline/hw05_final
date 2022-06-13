from django.test import TestCase

from posts.models import Group, Post, User


class CommonModelsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test group',
            description="Test description"
        )
        cls.post = Post.objects.create(
            text='Начинаем тестировать проект!',
            author=User.objects.create(),
        )

    def test_str_post(self):
        post = self.post
        expected_str = post.text[:15]
        self.assertEquals(expected_str, str(post))

    def test_str_group(self):
        group = self.group
        expected_str = group.title
        self.assertEquals(expected_str, str(group))
