from django.forms import ModelForm
from blurber.models import Review


class ReviewForm(ModelForm):

    class Meta:
        model = Review
        fields = ['blurb', 'score']
