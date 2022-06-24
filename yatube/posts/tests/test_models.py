from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Group, Post, Comment


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись, придуманная автором',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Крутой пост!!!!!!!!!!!!!',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        comment = PostModelTest.comment
        field_verboses = {
            post.text[:15]: str(post),
            group.title: str(group),
            comment.text[:15]: str(comment)
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)
