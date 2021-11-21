from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from posts.models import Group, Post

User = get_user_model()


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Test',
            slug='test_slug',
            description='testing',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test_group',
            group=cls.group,
        )

    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (reverse(
                'posts:group_list', kwargs={'slug': 'test_slug'})),
            'posts/profile.html': (reverse(
                'posts:profile', kwargs={'username': 'StasBasov'})),
            'posts/post_detail.html': (reverse(
                'posts:post_detail', args='1')),
            'posts/create_post.html': (reverse(
                'posts:post_edit', args={'slug': 'test-slug'})),
            'posts/create_post.html': reverse('posts:create_post'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:create_post'))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for name, expected in form_fields.items():
            with self.subTest(name=name):
                field_filled = response.context.get("form").fields.get(name)
                self.assertIsInstance(field_filled, expected)

    def test_edit_page_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit', args='1'))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for name, expected in form_fields.items():
            with self.subTest(name=name):
                field_filled = response.context.get("form").fields.get(name)
                self.assertIsInstance(field_filled, expected)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        post = response.context["page_obj"][0]
        self.assertEqual(post, self.post)

    def test_group_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[self.group.slug]))
        self.assertEqual(response.context["group"], self.group)
        self.assertIn("page_obj", response.context)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', args=[self.user.username]))
        self.assertEqual(response.context['user'], self.user)
        self.assertIn('page_obj', response.context)

    def test_post_edit_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', args='1'))
        self.assertIn("form", response.context)
        self.assertEqual(response.context["post"], self.post)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='posts_author',
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.post = [
            Post.objects.create(
                text='Пост №' + str(i),
                author=PaginatorViewsTest.user,
                group=PaginatorViewsTest.group
            )
            for i in range(13)]

        def setUp(self):
            self.user = User.objects.create_user(username='DanBasov')
            self.authorized_client = Client()
            self.authorized_client.force_login(self.user)

        def first_page_paginator_index(self):
            response = self.client.get(reverse('posts:index'))
            self.assertEqual(len(response.context['object_list']), 10)

        def second_page_index_paginator(self):
            response = self.client.get(reverse('posts:index') + '?page=2')
            self.assertEqual(len(response.context['object_list']), 3)

        def test_paginator_on_pages(self):
            first_page_len_posts = 10 
            second_page_len_posts = 3
            context = {
                reverse('posts:index'): first_page_len_posts,
                reverse('posts:index') + '?page=2': second_page_len_posts,
                reverse(
                    'posts:group_list', kwargs={
                        'slug': self.group.slug,}):
                first_page_len_posts,
                reverse(
                    'posts:group_list', kwargs={
                        'slug': self.group.slug,})
                + '?page=2': second_page_len_posts,
                reverse(
                    'posts:profile', kwargs={
                        'username': self.user.username}):
                first_page_len_posts,
                reverse(
                    'posts:profile', kwargs={
                        'username': self.user.username})
                + '?page=2': second_page_len_posts,
            }
            for reverse_page, len_posts in context.items():
                with self.subTest(reverse=reverse):
                    self.assertEqual(len(self.client.get(
                        reverse_page).context.get('page')), len_posts)
