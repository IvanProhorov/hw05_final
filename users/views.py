from django.urls import reverse_lazy
from django.views.generic import CreateView
import  datetime as dt
from .forms import CreationForm


class SignUp(CreateView):
        form_class = CreationForm
        success_url = "/auth/login/"
        template_name = "templatetags/signup.html"
