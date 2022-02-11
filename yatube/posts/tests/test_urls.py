from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Group, Post, User


INDEX = reverse('posts:index')
CREATE_POST = reverse('posts:create_post')
AUTH_LOGIN = reverse('login')
SLUG = 'testgroup'
GROUP_URL = reverse('posts:group_list', kwargs={'slug': SLUG})
TEST_404 = 'about/___'


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.user2 = User.objects.create(username='USERNAME2')
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
        cls.PROFILE_URL = reverse(
            'posts:profile', args=[cls.user.username])

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
            self.PROFILE_URL: 'posts/profile.html',
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
            [INDEX, self.guest_client, 200],
            [CREATE_POST, self.authorized_client, 200],
            [GROUP_URL, self.guest_client, 200],
            [self.POST_URL, self.guest_client, 200],
            [self.PROFILE_URL, self.guest_client, 200],
            [TEST_404, self.authorized_client, 404],
        ]
        for url, client, status in urls_names:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code, status)
