from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
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
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group(self):
        response = self.guest_client.get('/group/test_slug/')
        self.assertEqual(response.status_code, 200)

    def test_profile(self):
        response = self.guest_client.get('/profile/NoName/')
        self.assertEqual(response.status_code, 200)

    def test_author(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_tech(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_new_post_page_redirect(self):
        response = self.guest_client.get('/create/', follow=False)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_404(self):
        response = self.authorized_client.get('about/___')
        self.assertEqual(response.status_code, 404)

    def test_post_detail(self):
        response = self.guest_client.get('/posts/1/')
        self.assertEqual(response.status_code, 200)

    def test_create_post_author(self):
        response = self.authorized_client.get('/posts/1/edit/', username=True)
        self.assertEqual(response.status_code, 200)
