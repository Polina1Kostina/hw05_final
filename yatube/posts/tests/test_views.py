from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group, Comment, Follow
from django import forms
from django.shortcuts import get_list_or_404, get_object_or_404
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache


User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='HasName')
        cls.user_2 = User.objects.create(username='HasNoName')
        cls.user_3 = User.objects.create(username='NewName')
        Group.objects.bulk_create([
            Group(title='first', description='Описание', slug='slug1', pk=1),
            Group(title='second', description='Описание', slug='slug2', pk=2),
        ])
        cls.group = Group.objects.all()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_2 = Client()
        cls.authorized_client_2.force_login(cls.user_2)
        cls.authorized_client_3 = Client()
        cls.authorized_client_3.force_login(cls.user_3)
        cls.guest_client = Client()
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
        Post.objects.bulk_create([
            Post(text='Тестовый текст1',
                 group=cls.group[0],
                 author=cls.user,
                 image=uploaded,
                 pk=1),
            Post(text='Тестовый текст2',
                 group=cls.group[0],
                 author=cls.user,
                 pk=2),
            Post(text='Тестовый текст3',
                 group=cls.group[1],
                 author=cls.user,
                 pk=3),
            Post(text='Тестовый текст4',
                 group=cls.group[1],
                 author=cls.user,
                 pk=4)
        ])
        Comment.objects.create(
            post=get_object_or_404(Post, pk=4),
            author=cls.user,
            text='Крутой пост!'
        )
        Follow.objects.create(
            user=cls.user_2,
            author=cls.user
        )

    def setUp(self):
        cache.clear()

    def test_pages_uses_correct_template_authorized_client(self):
        """URL-адреса используют соответствующии шаблоны
        для авторизованного пользователя."""
        self.post_all = Post.objects.all()
        for self.post in self.post_all:
            templates_pages_names = {
                reverse('posts:index'): 'posts/index.html',
                reverse('posts:group_list', kwargs={
                    'slug': self.post.group.slug}): 'posts/group_list.html',
                reverse(
                    'posts:profile', kwargs={
                        'username': self.post.author.username}
                ): 'posts/profile.html',
                reverse('posts:post_detail', kwargs={
                    'post_id': self.post.pk}): 'posts/post_detail.html',
                reverse('posts:post_edit', kwargs={'post_id': self.post.pk}): (
                    'posts/post_create.html'
                ),
                reverse('posts:post_create'): 'posts/post_create.html',
                reverse('posts:follow_index'): 'posts/follow.html',
            }
            for reverse_name, template in templates_pages_names.items():
                with self.subTest(reverse_name=reverse_name):
                    response = self.authorized_client.get(reverse_name)
                    cache.clear()
                    self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template_guest_client(self):
        """URL-адреса используют соответствующии шаблоны
        для неавторизованного пользователя."""
        self.post_all = Post.objects.all()
        for self.post in self.post_all:
            templates_pages_names = {
                reverse('posts:index'): 'posts/index.html',
                reverse('posts:group_list', kwargs={
                    'slug': self.post.group.slug}): 'posts/group_list.html',
                reverse(
                    'posts:profile', kwargs={
                        'username': self.post.author.username}
                ): 'posts/profile.html',
                reverse('posts:post_detail', kwargs={
                    'post_id': self.post.pk}): 'posts/post_detail.html',
            }
            for reverse_name, template in templates_pages_names.items():
                with self.subTest(reverse_name=reverse_name):
                    response = self.guest_client.get(reverse_name)
                    cache.clear()
                    self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['posts'][0]
        self.post = Post.objects.all()
        context_objects = {
            first_object.author.username: self.post[0].author.username,
            first_object.text: self.post[0].text,
            first_object.group.title: self.post[0].group.title,
            first_object.image: self.post[0].image,
        }
        for response_name, reverse_name in context_objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 4})
        )
        self.assertEqual(Post.objects.get(id=4), response.context['posts'])
        self.assertEqual(
            Comment.objects.get(id=1), response.context['comments'][0]
        )

    def test_posts_page_show_correct_context(self):
        """Шаблоны profile, follow и group_list сформированы"""
        """с правильным контекстом."""
        self.author = get_object_or_404(User, username=self.user)
        self.group = get_object_or_404(Group, slug='slug1')
        objects = {
            reverse('posts:profile', kwargs={'username': self.user}): (
                self.author.name.select_related('author')
            ),
            reverse('posts:group_list', kwargs={'slug': 'slug1'}): (
                self.group.post.select_related('group')
            ),
            reverse('posts:follow_index'): (
                Post.objects.filter(author__following__user=self.user_2)
            ),
        }
        for reverse_name, response_name in objects.items():
            response = self.authorized_client.get(reverse_name)
            with self.subTest(reverse_name=reverse_name):
                self.assertQuerysetEqual(response.context['posts'], (
                    map(repr, response_name))
                )

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_form(self):
        """Форма post_edit сформирована с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_cache_index(self):
        """На странице index список записей кешируется на 20 секунд."""
        post = get_object_or_404(Post, id=1)
        response_1 = self.client.get(reverse('posts:index'))
        post.delete()
        response_2 = self.client.get(reverse('posts:index'))
        self.assertEqual(response_1.content, response_2.content)

    def test_posts_page_show_correct_context(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
        подписан и не появляется в ленте тех, кто не подписан."""
        reverse_name = 'posts:follow_index'
        response_1 = self.authorized_client_2.get(
            reverse(reverse_name)
        )
        self.new_post = Post.objects.create(
            text='Новый пост',
            group=self.group[0],
            author=self.user)
        response_2 = self.authorized_client_2.get(
            reverse(reverse_name)
        )
        self.assertEqual(
            len(response_1.context['page_obj']) + 1,
            len(response_2.context['page_obj'])
        )
        response_3 = self.authorized_client_3.get(
            reverse(reverse_name)
        )
        count_posts: int = 0
        self.assertEqual(len(response_3.context['page_obj']), count_posts)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create(username='Name')
        cls.user2 = User.objects.create(username='NoName')
        cls.guest_client = Client()
        cls.group1 = Group.objects.create(
            title='cats', description='Описание', slug='cat'
        )
        cls.group2 = Group.objects.create(
            title='dogs', description='Описание', slug='dogs'
        )
        article = []
        for i in range(7):
            article += [Post(text="Тестовый текст"
                        + str(i), group=cls.group1, author=cls.user1)]
            article += [Post(text="НеТестовый текст"
                        + str(i), group=cls.group2, author=cls.user2)]
        Post.objects.bulk_create(article)

    def setUp(self):
        cache.clear()

    def test_first_page_contains_ten_posts(self):
        """На первых страницах index, group_list, profile, follow выводится
        правильное количество постов"""
        posts_per_first_page_1: int = 10
        posts_per_first_page_2: int = 7
        objects = {
            reverse('posts:index'): posts_per_first_page_1,
            reverse('posts:group_list', kwargs={'slug': 'cat'}): (
                posts_per_first_page_2),
            reverse('posts:profile', kwargs={'username': self.user1}): (
                posts_per_first_page_2),
        }
        for reverse_name, numb in objects.items():
            response = self.guest_client.get(reverse_name)
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(len(response.context['page_obj']), numb)

    def test_second_page_contains_four_posts(self):
        """На второй странице index выводится 4 поста"""
        posts_per_second_page: int = 4
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), (
            posts_per_second_page)
        )


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create(username='Name')
        cls.user2 = User.objects.create(username='NoName')
        cls.user3 = User.objects.create(username='NewName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user1)

        cls.guest_client = Client()
        cls.group = Group.objects.create(
            title='cats', description='Описание', slug='cat'
        )
        Follow.objects.create(
            user=cls.user1,
            author=cls.user2
        )

    def test_follow_add_and_delete_authorized_client(self):
        """Авторизованный пользователь может подписываться
        на других пользователей и удалять их из подписок"""
        follow_count_1 = len(get_list_or_404(Follow, user=self.user1))
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': 'NewName'})
        )
        follow_count_2 = len(get_list_or_404(Follow, user=self.user1))
        self.assertEqual(follow_count_1 + 1, follow_count_2)
        self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': 'NewName'})
        )
        follow_count_3 = len(get_list_or_404(Follow, user=self.user1))
        self.assertEqual(follow_count_2 - 1, follow_count_3)
