import shutil
import tempfile
from http import HTTPStatus
from django.shortcuts import redirect
from posts.forms import PostForm
from posts.models import Post, Group, User
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
       
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
                title = 'Test',
                slug = 'test_slug',
                description = 'testing',

            )
        cls.post = Post.objects.create(
                author = cls.user,
                text = 'Test_post',
                group = cls.group,
            )
     
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()  
        
        form_data = {
            'text': 'Testing text',
            'group': self.group.id,
            
            
        }
        response = self.authorized_client.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True
        )
  
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('posts:profile', kwargs={'username': 'StasBasov'}))
        self.assertEqual(Post.objects.count(), post_count+1)
        
        self.assertTrue(
            Group.objects.filter(
                description='testing',
                slug='test_slug',
                title='Test',
            ).exists()
        )

    def test_post_edit(self):
         
        
        form_data = {
            'text': 'New testing text',
            'group': self.group.id,
            
            
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                        'post_id': self.post.id,
                        }),
            data=form_data,
            follow=True
        )
  
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': self.post.id,
            }))
        
        
        self.assertTrue(
            Group.objects.filter(
                description='testing',
                slug='test_slug',
                title='Test',
            ).exists()
        )