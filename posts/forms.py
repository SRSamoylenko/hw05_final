from django import forms

from posts.models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        error_messages = {
            'text': {
                'required': ('Поле текста записи не должно быть пустым '
                             'или состоять только из пробелов.'),
            },
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        error_messages = {
            'text': {
                'required': ('Комментарий не может быть пустым '
                             'или состоять только из пробелов.'),
            },
        }
