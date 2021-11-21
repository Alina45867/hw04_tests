from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()

class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.posts = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )


    def test_models_have_correct_object_names(self):
        task = PostModelTest.posts
        expected_object_name = task.text
        self.assertEqual(expected_object_name, str(task))
        task1 = PostModelTest.group
        expected_object_name1 = task1.title
        self.assertEqual(expected_object_name1, str(task))
