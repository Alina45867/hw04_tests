from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User

INDEX = reverse('posts:index')
SLUG = 'testgroup'
GROUP = reverse('posts:group_list', kwargs={'slug': SLUG})

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
        cls.group2 = Group.objects.create(
            title='Test2',
            slug='test_slug2',
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
                self.user.username, self.post.id])
        self.PROFILE = reverse(
            'posts:profile', args=[self.user.username])


    def test_post_in_url(self):
        urls_names = [
            GROUP,
            INDEX,
            self.POST_EDIT,
        ]
        for value in urls_names:
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                self.assertEqual(Post.objects.count(), 1)
                

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(self.PROFILE)
        self.assertEqual(response.context['user'], self.user)
        self.assertIn('page_obj', response.context)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='posts_author')
        posts = [Post(author=cls.user, text=str(i)) for i in range(POSTS)]
        Post.objects.bulk_create(posts)
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )


        def test_page_count_records(self):
            response = self.client.get(INDEX)
            self.assertEqual(
                len(response.context.get('page').object_list), POSTS
            )

        
