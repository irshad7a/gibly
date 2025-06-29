from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from .models import Profile, Post, Comment, like, Follow
from .forms import RegisterForm, PostForm, CommentForm

class SocialMediaAppTests(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='user1', password='pass1234', email='user1@example.com')
        self.user2 = User.objects.create_user(username='user2', password='pass1234', email='user2@example.com')
        # Create client
        self.client = Client()

    def test_register_valid(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123',
            'password2': 'ComplexPass123',
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_invalid(self):
        # Passwords do not match
        response = self.client.post(reverse('register'), {
            'username': 'baduser',
            'email': 'baduser@example.com',
            'password1': 'pass1234',
            'password2': 'pass5678',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The two password fields didn’t match")
        self.assertFalse(User.objects.filter(username='baduser').exists())

    def test_login_required_profile(self):
        response = self.client.get(reverse('profile_by_username', args=[self.user1.username]))
        self.assertRedirects(response, '/login/?next=' + reverse('profile_by_username', args=[self.user1.username]))
        self.client.login(username='user1', password='pass1234')
        response = self.client.get(reverse('profile_by_username', args=[self.user1.username]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user1.username)

    @patch('django.core.files.images.ImageFile')
    @patch('gibly.main.forms.PostForm.is_valid', return_value=True)
    @patch('gibly.main.forms.PostForm.save')
    def test_create_post(self, mock_save, mock_is_valid, mock_imagefile):
        self.client.login(username='user1', password='pass1234')
        # Mock image validation and form validation/save
        mock_imagefile.return_value = True
        mock_save.return_value = Post(user=self.user1, caption='Test caption')
        image_content = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
            b'\x00\x00\x00\nIDATx\xdac\xf8\x0f\x00\x01\x01\x01\x00'
            b'\x18\xdd\x8d\x18\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        image = SimpleUploadedFile(name='test_image.png', content=image_content, content_type='image/png')
        response = self.client.post(reverse('create_post'), {
            'caption': 'Test caption',
            'image': image,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_is_valid.called)
        self.assertTrue(mock_save.called)

    def test_post_detail_and_comment(self):
        self.client.login(username='user1', password='pass1234')
        post = Post.objects.create(user=self.user1, image='posts/test.jpg', caption='Test post')
        response = self.client.get(reverse('post_detail', args=[post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test post')

        response = self.client.post(reverse('post_detail', args=[post.id]), {
            'content': 'Nice post!',
        })
        self.assertRedirects(response, reverse('post_detail', args=[post.id]))
        self.assertTrue(Comment.objects.filter(user=self.user1, post=post, content='Nice post!').exists())

    def test_like_unlike_post(self):
        self.client.login(username='user1', password='pass1234')
        post = Post.objects.create(user=self.user2, image='posts/test.jpg', caption='Another post')
        # Like post
        response = self.client.get(reverse('like_post', args=[post.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(like.objects.filter(user=self.user1, post=post).exists())
        # Unlike post
        response = self.client.get(reverse('like_post', args=[post.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(like.objects.filter(user=self.user1, post=post).exists())

    def test_user_list_and_follow_unfollow(self):
        self.client.login(username='user1', password='pass1234')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user2.username)

        # Follow user2
        response = self.client.post(reverse('follow', args=[self.user2.id]))
        self.assertRedirects(response, reverse('profile_by_username', args=[self.user2.username]))
        self.assertTrue(Follow.objects.filter(follower=self.user1, following=self.user2).exists())

        # Unfollow user2
        response = self.client.post(reverse('unfollow', args=[self.user2.id]))
        self.assertRedirects(response, reverse('profile_by_username', args=[self.user2.username]))
        self.assertFalse(Follow.objects.filter(follower=self.user1, following=self.user2).exists())

        # Follow user2
        response = self.client.get(reverse('follow', args=[self.user2.id]))
        self.assertRedirects(response, reverse('user_list'))
        self.assertTrue(Follow.objects.filter(follower=self.user1, following=self.user2).exists())

        # Unfollow user2
        response = self.client.get(reverse('unfollow', args=[self.user2.id]))
        self.assertRedirects(response, reverse('user_list'))
        self.assertFalse(Follow.objects.filter(follower=self.user1, following=self.user2).exists())

        # Follow user2
        response = self.client.post(reverse('follow', args=[self.user2.id]))
        self.assertRedirects(response, reverse('profile_by_username', args=[self.user2.username]))
        self.assertTrue(Follow.objects.filter(follower=self.user1, following=self.user2).exists())

        # Unfollow user2
        response = self.client.post(reverse('unfollow', args=[self.user2.id]))
        self.assertRedirects(response, reverse('profile_by_username', args=[self.user2.username]))
        self.assertFalse(Follow.objects.filter(follower=self.user1, following=self.user2).exists())

        # Follow user2
        response = self.client.get(reverse('follow', args=[self.user2.id]))
        self.assertRedirects(response, reverse('profile_by_username', args=[self.user2.username]))
        self.assertTrue(Follow.objects.filter(follower=self.user1, following=self.user2).exists())

        # Unfollow user2
        response = self.client.get(reverse('unfollow', args=[self.user2.id]))
        self.assertRedirects(response, reverse('profile_by_username', args=[self.user2.username]))
        self.assertFalse(Follow.objects.filter(follower=self.user1, following=self.user2).exists())

    # Additional thorough tests

    def test_unauthenticated_access(self):
        # Test that unauthenticated users are redirected from protected views
        protected_urls = [
            reverse('profile_by_username', args=[self.user1.username]),
            reverse('create_post'),
            reverse('post_detail', args=[1]),
            reverse('like_post', args=[1]),
            reverse('user_list'),
            reverse('follow', args=[1]),
            reverse('unfollow', args=[1]),
        ]
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn('/login/', response.url)

    def test_post_detail_404(self):
        self.client.login(username='user1', password='pass1234')
        response = self.client.get(reverse('post_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_follow_self(self):
        self.client.login(username='user1', password='pass1234')
        response = self.client.post(reverse('follow', args=[self.user1.id]))
        self.assertRedirects(response, reverse('profile_by_username', args=[self.user1.username]))
        self.assertFalse(Follow.objects.filter(follower=self.user1, following=self.user1).exists())

    def test_unfollow_not_following(self):
        self.client.login(username='user1', password='pass1234')
        response = self.client.post(reverse('unfollow', args=[self.user2.id]))
        self.assertRedirects(response, reverse('profile_by_username', args=[self.user2.username]))
        self.assertFalse(Follow.objects.filter(follower=self.user1, following=self.user2).exists())

    def test_like_post_unauthenticated(self):
        post = Post.objects.create(user=self.user2, image='posts/test.jpg', caption='Test post')
        response = self.client.get(reverse('like_post', args=[post.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_comment_post_unauthenticated(self):
        post = Post.objects.create(user=self.user2, image='posts/test.jpg', caption='Test post')
        response = self.client.post(reverse('post_detail', args=[post.id]), {'content': 'Test comment'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_like_post_invalid_post(self):
        self.client.login(username='user1', password='pass1234')
        response = self.client.get(reverse('like_post', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_comment_post_invalid_post(self):
        self.client.login(username='user1', password='pass1234')
        response = self.client.post(reverse('post_detail', args=[9999]), {'content': 'Test comment'})
        self.assertEqual(response.status_code, 404)
