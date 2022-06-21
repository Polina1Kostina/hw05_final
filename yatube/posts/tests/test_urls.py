from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group


User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create(username='HasNoName')
        cls.user2 = User.objects.create(username='HasName')
        cls.group = Group.objects.create(
            title='Название', description='Описание', slug='test-slug'
        )
        cls.authorized_client_1 = Client()
        cls.authorized_client_1.force_login(cls.user1)
        cls.authorized_client_2 = Client()
        cls.authorized_client_2.force_login(cls.user2)
        cls.guest_client = Client()
        Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user1
        )

    def test_post_list_url_exists_at_desired_location_guest_client(self):
        """Проверка доступности адресов для неавторизованного пользователя."""
        posts_urls = {
            '/': 'OK',
            '/group/test-slug/': 'OK',
            '/profile/HasNoName/': 'OK',
            '/posts/1/': 'OK',
            '/create/': 'Found',
            '/posts/1/edit/': 'Found',
            '/unexisting_page/': 'Not Found',
        }
        for address, st_code in posts_urls.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.reason_phrase, st_code)

    def test_post_list_url_exists_at_desired_location_authorized_client(self):
        """Проверка доступности адресов для авторизованного пользователя."""
        posts_urls = {
            '/': 'OK',
            '/group/test-slug/': 'OK',
            '/profile/HasNoName/': 'OK',
            '/posts/1/': 'OK',
            '/create/': 'OK',
            '/posts/1/edit/': 'OK',
            '/unexisting_page/': 'Not Found',
            '/posts/1/comment/': 'Found',
            '/profile/HasName/follow/': 'Found',
            '/profile/HasName/unfollow/': 'Found',
        }
        for address, st_code in posts_urls.items():
            with self.subTest(address=address):
                response = self.authorized_client_1.get(address)
                self.assertEqual(response.reason_phrase, st_code)

    def test_urls_redirect_anonymous_on_admin_login(self):
        """Страницы post_edit и post_creat перенаправят анонимного
        пользователя на страницу логина."""
        redirect_urls = {
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/',
            '/create/': '/auth/login/?next=/create/',
        }
        for address, url in redirect_urls.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, url)

    def test_post_edit_url_exists_at_desired_location(self):
        """Страница /posts/1/edit доступна автору поста."""
        response = self.authorized_client_1.get('/posts/1/edit/')
        self.assertEqual(response.reason_phrase, 'OK')

    def test_urls_uses_correct_templates(self):
        """URL-адреса используют соответствующии шаблоны."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            '/posts/1/edit/': 'posts/post_create.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/post_create.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_1.get(address)
                self.assertTemplateUsed(response, template)
