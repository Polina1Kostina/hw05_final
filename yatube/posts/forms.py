from .models import Post, Group, Comment
from django import forms


class PostForm(forms.ModelForm):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label="(Группа не выбрана)",
        label='Группа',
        required=False
    )

    class Meta:
        model = Post
        fields = ['text', 'group', 'image']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
