from django.forms import ModelForm, Form, FileField
from blurber.models import Review, Song


class ReviewForm(ModelForm):

    class Meta:
        model = Review
        fields = ['blurb', 'score']


class UploadSongForm(ModelForm):

    class Meta:
        model = Song
        fields = ['artist', 'title', 'youtube_link', 'web_link', 'mp3_link', 'mp3_file']
