from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user
from posts.models import Group, Post, User
from yatube.settings import NUMBER_POSTS

INDEX = reverse('posts:index')
SLUG = 'test_slug'
GROUP = reverse('posts:group_list', kwargs={'slug': SLUG})
SLUG2 = 'testgroup2'
GROUP2 = reverse('posts:group_list', kwargs={'slug': SLUG2})
AUTHOR = 'posts_author'
PROFILE = reverse('posts:profile', args=[AUTHOR])


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
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
        cls.POST_EDIT = reverse('posts:post_edit', args=[
            cls.post.id])
        cls.POST_DETAIL = reverse('posts:post_detail', kwargs={
            'post_id': cls.post.id, })

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_page_show_correct_context(self):
        urls = [
            [INDEX, self.authorized_client],
            [self.POST_DETAIL, self.authorized_client],
            [PROFILE, self.authorized_client],
            [GROUP, self.authorized_client],
        ]
        for url, client in urls:
            with self.subTest(url=url, client=get_user(client).username):
                post = Post.objects.first()
                post_text_0 = post.text
                post_author_0 = post.author
                post_group_0 = post.group
                self.assertEqual(post_text_0, self.post.text)
                self.assertEqual(post_author_0, self.post.author)
                self.assertEqual(post_group_0, self.post.group)

    def test_post_not_in_group2(self):
        response_group = self.authorized_client.get(GROUP2)
        self.assertNotIn(self.post, response_group.context.get('page_obj'))

    def test_profile_show_correct_context(self):
        response = self.authorized_client.get(PROFILE)
        self.assertEqual(self.user, response.context.get('author'))

    def test_group_page_show_correct_context(self):
        response = self.authorized_client.get(GROUP)
        group = response.context.get('group')
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.description, self.group.description)
        self.assertEqual(group.slug, self.group.slug)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=AUTHOR)
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug=SLUG,
            description='Тестовое описание группы',
        )
        posts = [Post(
            author=cls.user, group=cls.group, text=str(i)) for i in range(13)]
        Post.objects.bulk_create(posts)

    def test_paginator_on_pages(self):
        first_page_len_posts = NUMBER_POSTS
        second_page_len_posts = 3
        context = {
            INDEX: first_page_len_posts,
            INDEX + '?page=2': second_page_len_posts,
            GROUP: first_page_len_posts,
            GROUP + '?page=2': second_page_len_posts,
            PROFILE: first_page_len_posts,
        }
        for reverse_page, len_posts in context.items():
            with self.subTest(reverse=reverse):
                self.assertEqual(len(self.client.get(
                    reverse_page).context.get('page_obj')), len_posts)
