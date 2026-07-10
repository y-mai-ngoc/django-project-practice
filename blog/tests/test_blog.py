"""
Blog tests - Models, Views, Forms
Run: python manage.py test blog
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import Post, Category, Comment
from blog.forms import PostForm, CommentForm


class CategoryModelTest(TestCase):
    def test_str_representation(self):
        category = Category.objects.create(name='Python', slug='python')
        self.assertEqual(str(category), 'Python')

    def test_auto_slug(self):
        category = Category(name='Web Development')
        category.save()
        self.assertEqual(category.slug, 'web-development')


class PostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        cls.category = Category.objects.create(
            name='Django', slug='django'
        )
        cls.post = Post.objects.create(
            title='Test Post About Django',
            slug='test-post-about-django',
            author=cls.user,
            category=cls.category,
            body='This is a comprehensive test post about Django framework.',
            status='published',
        )

    def test_str_representation(self):
        self.assertEqual(str(self.post), 'Test Post About Django')

    def test_get_absolute_url(self):
        url = self.post.get_absolute_url()
        self.assertEqual(url, '/post/test-post-about-django/')

    def test_default_status_is_draft(self):
        post = Post(title='Draft Post', author=self.user, body='Content')
        self.assertEqual(post.status, 'draft')

    def test_reading_time(self):
        # 200 words = 1 min
        self.assertGreaterEqual(self.post.reading_time, 1)

    def test_ordering(self):
        """Posts should be ordered by -published_at"""
        post2 = Post.objects.create(
            title='Newer Post', slug='newer-post',
            author=self.user, body='Content', status='published'
        )
        posts = list(Post.objects.all())
        self.assertEqual(posts[0], post2)  # Newer first


class PostViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.post = Post.objects.create(
            title='Published Post', slug='published-post',
            author=self.user, body='Content here.',
            status='published'
        )

    def test_post_list_status_code(self):
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)

    def test_post_list_template(self):
        response = self.client.get(reverse('blog:post_list'))
        self.assertTemplateUsed(response, 'blog/post_list.html')

    def test_post_list_contains_post(self):
        response = self.client.get(reverse('blog:post_list'))
        self.assertContains(response, 'Published Post')

    def test_draft_post_not_in_list(self):
        Post.objects.create(
            title='Draft Post', slug='draft-post',
            author=self.user, body='Draft content.',
            status='draft'
        )
        response = self.client.get(reverse('blog:post_list'))
        self.assertNotContains(response, 'Draft Post')

    def test_post_detail_status_code(self):
        response = self.client.get(
            reverse('blog:post_detail', kwargs={'slug': 'published-post'})
        )
        self.assertEqual(response.status_code, 200)

    def test_post_create_requires_login(self):
        response = self.client.get(reverse('blog:post_create'))
        self.assertEqual(response.status_code, 302)

    def test_post_create_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blog:post_create'))
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        response = self.client.get(
            reverse('blog:post_list') + '?q=Published'
        )
        self.assertContains(response, 'Published Post')


class CommentFormTest(TestCase):
    def test_valid_comment_form(self):
        form = CommentForm(data={
            'author_name': 'Test User',
            'email': 'test@example.com',
            'body': 'This is a great post!',
        })
        self.assertTrue(form.is_valid())

    def test_invalid_comment_form_empty_body(self):
        form = CommentForm(data={
            'author_name': 'Test User',
            'email': 'test@example.com',
            'body': '',
        })
        self.assertFalse(form.is_valid())

    def test_invalid_comment_form_bad_email(self):
        form = CommentForm(data={
            'author_name': 'Test User',
            'email': 'not-an-email',
            'body': 'Comment text',
        })
        self.assertFalse(form.is_valid())
