from django.forms import ModelForm, ValidationError, TextInput, Textarea
from tsj.models import Comment


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['name', 'mail', 'website', 'comment_text']
        widgets = {
            'name': TextInput(attrs={'size': 40}),
            'mail': TextInput(attrs={'size': 40}),
            'website': TextInput(attrs={'size': 40}),
            'comment_text': Textarea(attrs={'cols': 60, 'rows': 10})
        }
