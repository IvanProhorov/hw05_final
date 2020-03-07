from django.urls import path
from . import views
from django.conf.urls import handler404, handler500

#handler404 = "posts.views.page_not_found"
#handler500 = "posts.views.server_error"

urlpatterns = [
        # path() для страницы регистрации нового пользователя
        # её полный адрес будет auth/signup/, но префикс auth/ обрабатывется в головном urls.py
        path("signup/", views.SignUp.as_view(), name="signup")
]