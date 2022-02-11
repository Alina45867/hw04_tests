from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User

INDEX = reverse('posts:index')
SLUG = 'testgroup'
GROUP = reverse('posts:group_list', kwargs={'slug': SLUG})
SLUG2 = 'testgroup2'
GROUP2 = reverse('posts:group_list', kwargs={'slug': SLUG2})


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Test',
            slug=SLUG,
            description='testing',
        )
        cls.group2 = Group.objects.create(
            title='Test2',
            slug=SLUG2,
            description='testing2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test_group',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.POST_EDIT = reverse('posts:post_edit', args=[
            self.post.id])
        self.PROFILE = reverse(
            'posts:profile', args=[self.user.username])
        self.POST_DETAIL = reverse('posts:post_detail', kwargs={
            'post_id': self.post.id, })

    def test_post_in_url(self):
        urls_names = [
            GROUP,
            INDEX,
            self.PROFILE,
        ]
        for value in urls_names:
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                self.assertEqual(Post.objects.count(), 1)
                self.assertEqual(self.post,
                                 response.context['page_obj'][0])

    def test_post_not_in_group2(self):
        response_group = self.authorized_client.get(GROUP2)
        self.assertNotIn(self.post, response_group.context.get('page_obj'))


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='posts_author')
        posts = [Post(author=cls.user, text=str(i)) for i in range(13)]
        Post.objects.bulk_create(posts)
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )

        def test_paginator_on_pages(self):
            first_page_len_posts = 10
            second_page_len_posts = 3
            context = {
                INDEX: first_page_len_posts,
                INDEX + '?page=2': second_page_len_posts,
                GROUP: first_page_len_posts,
                GROUP + '?page=2': second_page_len_posts,
                self.PROFILE: first_page_len_posts,
                self.PROFILE + '?page=2': second_page_len_posts,
            }
            for reverse_page, len_posts in context.items():
                with self.subTest(reverse=reverse):
                    self.assertEqual(len(self.client.get(
                        reverse_page).context.get('page')), len_posts)
