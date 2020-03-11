from .models import Post, Comment
from django.forms import ModelForm


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ("group", "text", "image")
        labels = {
            "group": "Сообщества",
            "text": "Текст записи",
            "image":"Изображение",
        }
class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)