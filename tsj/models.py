from django.db import models
from blurber.models import Song


class PublicPost(models.Model):
    """
    A 'cached' copy of the song and its reviews that is
    visible on the public site.
    This allows quicker searching until a proper search function can be built.
    """
    song = models.ForeignKey(Song)
    html_content = models.TextField(help_text="Only edit this in an emergency!")
    visible = models.BooleanField(default=True)
    include_in_search_results = models.BooleanField(default=True)
    published_on = models.DateField()

    def __str__(self):
        self.song.__str__()
