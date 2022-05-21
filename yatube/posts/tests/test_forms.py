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
        cls.POST_DETAIL = reverse('posts:post_detail', kwargs={
            'post_id': cls.post.id, })
        cls.POST_EDIT = reverse('posts:post_edit', kwargs={
            'post_id': cls.post.id})
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

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
                    field_filled = (
                        response.context.get("form").fields.get(name))
                    self.assertIsInstance(field_filled, expected)

    def test_create_post(self):
        post = Post.objects.first()
        post.delete()
        post = Post.objects.count()
        form_data = {
            'text': 'Nothing',
            'group': self.group.id,

        }
        response = self.authorized_client.post(
            CREATE_POST,
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, PROFILE)
        self.assertEqual(Post.objects.count(), post + 1)
        post = response.context['page_obj'][0]
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.post.author)

    def test_post_edit(self):
        post = Post.objects.count()
        form_data = {
            'text': 'Nothing2',
            'group': self.group2.id,
        }
        response = self.authorized_client.post(
            self.POST_EDIT,
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), post)
        post = response.context['post']
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, self.group2)
        self.assertEqual(post.author, self.post.author)
