from django.core.cache import cache

from django.contrib.auth.models import User
from django.core.cache.utils import make_template_fragment_key
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, Follow


class TestPosts(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="admin", email="admin.s@skynet.com", password="admin"
        )
        self.client.login(username='admin', password='admin')
        self.urls = {'/', reverse("profile", kwargs={'username': 'admin'}),
                     reverse("post", kwargs={'username': 'admin', "post_id": 1})}

    def text_on_all_pages(self, text):
        for url in self.urls:
            response = self.client.get(url)
            if url == self.urls[2]:
                text_response_posts = response.context['post'].text
            else:
                text_response_posts = response.context['posts'][0].text
            self.assertEquals(text_response_posts, text)

    def test_new_post(self):

         response = self.client.post(reverse("new_post"),
                                    {'text': 'Тест добавления записи'}, follow=True)
         self.assertEqual(response.status_code, 200)

    def test_new_post_unauthorized_user(self):
        self.client = Client()
        response = self.client.post(
            reverse("new_post"), {'text': 'test'}, follow=True)
        self.assertRedirects(response, "/auth/login/?next=%2Fnew%2F")

    def test_update_info_when_create_new_post(self):
        self.client.post(reverse("new_post"),
                         {'text': 'Тест добавления записи'}, follow=True)
        self.text_on_all_pages('Тест добавления записи')

    def test_edit_post(self):
        user_profile = User.objects.get(username='admin')
        post = Post.objects.filter(author=user_profile).order_by('-pub_date').first()
        self.client.post(reverse("post_edit", kwargs={'username': 'admin', "post_id": 1}),
                         {'text': 'Тест добавления записи 1'}, follow=True)
        self.text_on_all_pages('Тест добавления записи 1')


class PostsImgTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test", email="test.s@skynet.com", password="test"
        )
        self.group = Group.objects.create(title='TestGroup',
                                     slug='testgroup',
                                     description='test')
        self.client.login(username='test', password='test')

    def test_img_upload(self):
        with open('1.jpg', 'rb') as fp:
            self.client.post('/new/', {'group':1, 'text':'Test post', 'image':fp,})
        for url in {'/test/1/','/','/test/','/group/testgroup/'}:
            response = self.client.get(url)
            self.assertContains(response, '<img', status_code=200)

    def test_file_upload(self):
        with open('README.md', 'rb') as fp:
            response = self.client.post('/new/', {'group':1, 'text':'Test post', 'image':fp,})
        self.assertFormError(response, 'form', 'image','no image file')

    def test_cache(self):
        key = make_template_fragment_key('index_page', [1])
        self.assertFalse(cache.get(key))
        self.client.get("/")
        self.assertTrue(cache.get(key))


    def test_follow(self):
        user = User.objects.create_user(
            username="test2", email="test2.s@skynet.com", password="test"
        )
        self.client.get("/test2/follow")
        favorite_list = Follow.objects.select_related('author', 'user').filter(user=self.user)
        self.assertEquals(len(favorite_list), 1)
        self.client.get("/test2/unfollow")
        favorite_list = Follow.objects.select_related('author', 'user').filter(user=self.user)
        self.assertEquals(len(favorite_list), 0)

    def test_comments(self):
        self.client.post('/new/', {'text': 'Test post'})
        add_comment_url = reverse('add_comment', args=['test', 1])
        response = self.client.get(add_comment_url,{'text':'comment'}, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.redirect_chain[0][0], '/test/1/')
        self.client.logout()
        self.client=Client()
        response = self.client.get(add_comment_url,{'text':'comment'}, follow=True)
        self.assertEquals(response.redirect_chain[0][0], '/auth/login/?next=/test/1/comment/%3Ftext%3Dcomment')

    def test_new_post_follow(self):
        user1 = User.objects.create_user(
            username="test2", email="test2.s@skynet.com", password="test"
        )
        user2 = User.objects.create_user(
            username="test3", email="test3.s@skynet.com", password="test"
        )
        self.client.get("/test3/follow")
        self.client.logout()
        self.client.login(username='test3', password='test')
        self.client.post('/new/', {'text': 'Test post'})
        self.client.logout()
        self.client.login(username='test', password='test')
        response = self.client.get('/follow/')
        print(response.context['post'])
        self.assertEquals(response.context['post'].text, 'Test post')
        self.client.logout()
        self.client.login(username='test2', password='test')
        response = self.client.get('/follow/')
        self.assertNotContains(response, 'post')