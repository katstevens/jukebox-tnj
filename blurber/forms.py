from django.forms import ModelForm, ValidationError, ChoiceField, IntegerField
from django.forms import modelformset_factory
from django.forms.widgets import Select
from blurber.models import Review, Song

BANNED_CLICHES = [
    'Cathedral of Sound',
    'Sounds like a young Kate Bush',
    'on acid',
    'songstress',
    'bargain bin Rihanna'
]

SCORE_RANGE = [
    (i, str(i)) for i in range(0, 11)
]


class ReviewForm(ModelForm):

    class Meta:
        model = Review
        fields = ['blurb', 'score']

    score = ChoiceField(widget=Select, choices=SCORE_RANGE)

    def clean_blurb(self):
        if self.cleaned_data['blurb'] == '<br>':
            raise ValidationError('Please enter a blurb.')
        lower_case_blurb = self.cleaned_data['blurb'].lower()
        for bc in BANNED_CLICHES:
            if bc in lower_case_blurb:
                raise ValidationError('Please think more carefully about your choice of words.')
        return self.cleaned_data['blurb']


class UploadSongForm(ModelForm):

    class Meta:
        model = Song
        fields = ['artist', 'title', 'youtube_link', 'web_link', 'mp3_link', 'mp3_file']


class SortReviewForm(ModelForm):

    class Meta:
        model = Review
        fields = ['sort_order']

    def __init__(self, *args, **kwargs):
        # This doesn't seem to work with the formset.
        super(SortReviewForm, self).__init__(*args, **kwargs)
        self.fields['sort_order'].required = True


SortReviewsFormSet = modelformset_factory(
    Review,
    form=SortReviewForm,
    extra=0
)
