from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user
from posts.models import Group, Post, User


INDEX = reverse('posts:index')
CREATE_POST = reverse('posts:create_post')
AUTH_LOGIN = reverse('login')
USERNAME = 'user'
USERNAME2 = 'USERNAME2'
SLUG = 'testgroup'
GROUP_URL = reverse('posts:group_list', kwargs={'slug': SLUG})
TEST_404 = 'about/___'
PROFILE_URL = reverse('posts:profile', kwargs={'username': USERNAME})
AUTH_LOGIN = reverse('login')


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user2 = User.objects.create(username=USERNAME2)
        cls.group = Group.objects.create(
            slug=SLUG,
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )
        cls.POST_URL = reverse('posts:post_detail',
                               args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit',
                                    args=[cls.post.id])
        cls.POST_NOT_AUTHOR = f'{AUTH_LOGIN}?next={CREATE_POST}'
        cls.REDIRECT_POST_EDIT = f'{AUTH_LOGIN}?next={cls.POST_EDIT_URL}'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            INDEX: 'posts/index.html',
            GROUP_URL: 'posts/group_list.html',
            PROFILE_URL: 'posts/profile.html',
            self.POST_URL: 'posts/post_detail.html',
            self.POST_EDIT_URL: 'posts/create_post.html',
            CREATE_POST: 'posts/create_post.html',
        }
        for adress, template in templates_pages_names.items():
            with self.subTest(adress=adress):
                self.assertTemplateUsed(self.authorized_client.get(adress),
                                        template)

    def test_urls_status_code(self):
        urls_names = [
            [self.POST_EDIT_URL, self.authorized_client2, 302],
            [self.POST_EDIT_URL, self.guest_client, 302],
            [self.POST_EDIT_URL, self.authorized_client, 200],
            [INDEX, self.guest_client, 200],
            [CREATE_POST, self.authorized_client, 200],
            [CREATE_POST, self.guest_client, 302],
            [GROUP_URL, self.guest_client, 200],
            [self.POST_URL, self.guest_client, 200],
            [PROFILE_URL, self.guest_client, 200],
            [TEST_404, self.authorized_client, 404],
        ]
        for url, client, status in urls_names:
            with self.subTest(url=url, client = get_user(client).username):
                self.assertEqual(client.get(url).status_code, status)

    def test_redirects(self):
        urls_names = [
            [CREATE_POST, self.guest_client,
                self.POST_NOT_AUTHOR],
            [self.POST_EDIT_URL, self.guest_client,
             self.REDIRECT_POST_EDIT],
            [self.POST_EDIT_URL, self.authorized_client2, self.POST_URL],
        ]
        for url, client, redirect in urls_names:
            with self.subTest(url=url, client = get_user(client).username):
                self.assertRedirects(client.get(url, follow=True), redirect)
