from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group, Comment
from django.core.files.uploadedfile import SimpleUploadedFile


User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='HasName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.guest_client = Client()
        cls.group = Group.objects.create(
            title='first', description='Описание', slug='slug'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
        )

    def test_create_post_authorized_client(self):
        """С валидной формы создаётся запись поста
        для авторизованного пользователя."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post_authorized_client(self):
        """Авторизованный пользователь редактирует пост с валидной формой."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )
        edit_post = Post.objects.get(id=1)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': 1})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(edit_post.text, form_data['text'])

    def test_create_and_edit_post_guest_client(self):
        """Запись поста не создаётся и не редактируется
        для неавторизованного пользователя."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст22222',
            'image': uploaded,
        }
        objects = {
            reverse('posts:post_create'): '/auth/login/?next=/create/',
            reverse('posts:post_edit', kwargs={'post_id': 1}): (
                '/auth/login/?next=/posts/1/edit/'
            ),
        }
        for reverse_name, redirect_url in objects.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.post(
                    reverse_name,
                    data=form_data,
                    follow=True
                )
                self.assertRedirects(response, redirect_url)
                self.assertEqual(Post.objects.count(), posts_count)

    def test_comment_post_authorized_client(self):
        """Авторизованный пользователь комментирует пост с валидной формой."""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Классный пост!!',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )
        add_comment = Comment.objects.get(id=1)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': 1})
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertEqual(add_comment.text, form_data['text'])
