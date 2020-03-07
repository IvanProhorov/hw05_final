from linecache import cache

from django.contrib.auth.models import User
from django.core.cache.utils import make_template_fragment_key
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group


class TestPosts(TestCase):

    def SetUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="admin", email="admin.s@skynet.com", password="admin"
        )
        self.client.login(username='admin', password='admin')
        self.urls = {'/', reverse("profile", kwargs={'username': 'admin'}),
                     reverse("post", kwargs={'username': 'admin', "post_id": 1})}
    #
    # def text_on_all_pages(self, text):
    #     for url in self.urls:
    #         response = self.client.get(url)
    #         if url == self.urls[2]:
    #             text_response_posts = response.context['post'].text
    #         else:
    #             text_response_posts = response.context['posts'][0].text
    #         self.assertEquals(text_response_posts, text)
    #
     # def test_new_post(self):
     #
     #     response = self.client.post(reverse("new_post"),
     #                                {'text': 'Тест добавления записи'}, follow=True)
     #     self.assertEqual(response.status_code, 200)
    #
    # def test_new_post_un_auth_user(self):
    #     self.client = Client()
    #     response = self.client.post(
    #         reverse("new_post"), {'text': 'test'}, follow=True)
    #
    #     self.assertRedirects(response, "/auth/login/?next=%2Fnew%2F")
    #
    # def test_update_info_when_create_new_post(self):
    #     self.client.post(reverse("new_post"),
    #                      {'text': 'Тест добавления записи'}, follow=True)
    #     self.text_on_all_pages('Тест добавления записи')
    #
    # def test_edit_post(self):
    #     user_profile = User.objects.get(username='admin')
    #     post = Post.objects.filter(author=user_profile).order_by('-pub_date').first()
    #     self.client.post(reverse("post_edit", kwargs={'username': 'admin', "post_id": 1}),
    #                      {'text': 'Тест добавления записи 1'}, follow=True)
    #     self.text_on_all_pages('Тест добавления записи 1')


class PostsImgTest(TestCase):
    def setUp(self):
        self.client = Client()
        user = User.objects.create_user(
            username="admin", email="admin.s@skynet.com", password="admin"
        )
        self.group = Group.objects.create(title='TestGroup',
                                          slug='testgroup',
                                          description='test')
        self.client.login(username='admin', password='admin')
    def test_img_upload(self):
        with open('1.jpg', 'rb') as fp:
            self.client.post('/new/', {'group':1, 'text':'Test post', 'image':fp,})
       # cache.clear()
        response = self.client.get('/admin/1/')
        self.assertContains(response, '<img', status_code=200)
        response = self.client.get('/')
        self.assertContains(response, '<img', status_code=200)
        response = self.client.get('/admin/')
        self.assertContains(response, '<img', status_code=200)
        response = self.client.get('/group/testgroup/')
        self.assertContains(response, '<img', status_code=200)

    def test_file_upload(self):
        with open('README.md', 'rb') as fp:
            response = self.client.post('/new/', {'group':1, 'text':'Test post', 'image':fp,})
        self.assertFormError(response, 'form', 'image', "Файл, который вы загрузили не является изображением.")
    def test_cashe(self):
        key = make_template_fragment_key('index_page',[1])
        self.assertFalse(cache.get(key))
        self.client.get("")
        self.assertTrue(cache.get(key))