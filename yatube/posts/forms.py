from django.forms import ModelForm
from django import forms
from .models import Post, Comment, Follow


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image']
        labels = {
            'group': 'Группа',
            'text': 'Текст',
            'image': 'Картинка'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'cols': 30, 'rows': 5})
        }


class FollowForm(ModelForm):
    class Meta:
        model = Follow
        labels = {'user': 'Подписка на:', 'author': 'Автор записи'}
        fields = ['user']
