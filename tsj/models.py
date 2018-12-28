from django.db import models
from blurber.models import Song


class PublicPost(models.Model):
    """
    A 'cached' copy of the song and its reviews that is
    visible on the public site.
    This allows quicker searching until a proper search function can be built.

    You can reopen then republish a song and create a new PublicPost which will hide the old one, or for small
    emergency changes you can edit the html_content directly.

    IMPORTANT: Song ID refers to the Song.id, not PublicPost.id (which may change if republished)
    """
    song = models.ForeignKey(Song)
    html_content = models.TextField(help_text="Only edit this in an emergency!")
    visible = models.BooleanField(default=True)
    include_in_search_results = models.BooleanField(default=True)
    published_on = models.DateTimeField()  # Don't edit this or use for scheduling, use Song.publish_date

    def __str__(self):
        return self.song.__str__()


class Comment(models.Model):
    song = models.ForeignKey(Song)
    name = models.CharField(max_length=100)
    mail = models.CharField(max_length=100)
    website = models.CharField(max_length=100, null=True, blank=True)
    comment_text = models.TextField()
    visible = models.BooleanField(default=True)
    published_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
