from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User

CREATE_POST = reverse('posts:create_post')
USERNAME = 'user'
PROFILE = reverse('posts:profile', kwargs={'username': USERNAME})


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title='Test',
            slug='test_slug',
            description='testing',
        )
        cls.group2 = Group.objects.create(
            title='Test2',
            slug='Tests2',
            description='Описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test_post',
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.POST_DETAIL = reverse('posts:post_detail', kwargs={
            'post_id': self.post.id, })
        self.POST_EDIT = reverse('posts:post_edit', kwargs={
            'post_id': self.post.id})

    def test_new_page_show_correct_context(self):
        urls_names = [
            CREATE_POST,
            self.POST_EDIT,
        ]
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for url in urls_names:
            response = self.authorized_client.get(url)
            for name, expected in form_fields.items():
                with self.subTest(name=name):
                    field_filled = response.context.get("form").fields.get \
                        (name)
                    self.assertIsInstance(field_filled, expected)

    def test_create_post(self):
        post = Post.objects.count()
        group = PostFormTests.group
        form_data = {
            'text': 'Testing text',
            'group': self.group.id,

        }
        response = self.authorized_client.post(
            CREATE_POST,
            data=form_data,
            follow=True
        )
        post1 = Post.objects.first()
        self.assertTrue(post1)
        self.assertEqual(Post.objects.count(), post + 1)
        self.assertEqual(post1.text, form_data['text'])
        self.assertEqual(post1.group, group)
        self.assertEqual(post1.author, self.user)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, PROFILE)

    def test_post_edit(self):
        group = PostFormTests.group2
        user = PostFormTests.user
        form_data = {
            'text': 'New testing text',
            'group': self.group2.id,
        }
        response = self.authorized_client.post(
            self.POST_EDIT,
            data=form_data,
            follow=True
        )
        post = response.context['post']
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, group)
        self.assertEqual(post.author, user)
        self.assertEqual(response.status_code, 200)
