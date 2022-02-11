from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User

CREATE_POST = reverse('posts:create_post')


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
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
        self.PROFILE = reverse(
            'posts:profile', args=[self.user.username])

    def test_new_page_show_correct_context(self):
        response = self.authorized_client.get(CREATE_POST)
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for name, expected in form_fields.items():
            with self.subTest(name=name):
                field_filled = response.context.get("form").fields.get(name)
                self.assertIsInstance(field_filled, expected)

    def test_edit_page_context(self):
        response = self.authorized_client.get(self.POST_EDIT)
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for name, expected in form_fields.items():
            with self.subTest(name=name):
                field_filled = response.context.get("form").fields.get(name)
                self.assertIsInstance(field_filled, expected)

    def test_create_post(self):
        post = Post.objects.count()
        form_data = {
            'text': 'Testing text',
            'group': self.group.id,

        }
        response = self.authorized_client.post(
            CREATE_POST,
            data=form_data,
            follow=True
        )
        post = response.context['page_obj'][0]
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.user)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.PROFILE)

    def test_post_edit(self):
        post = Post.objects.first()
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
        self.assertEqual(post.group, self.group2)
        self.assertEqual(post.author, self.user)
        self.assertEqual(response.status_code, 200)
