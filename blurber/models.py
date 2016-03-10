from __future__ import unicode_literals

from django.db import models

from writers.models import Writer

SONG_STATUS_CHOICES = (
    ('open', 'Open'),
    ('closed', 'Closed'),
    ('published', 'Published'),
    ('removed', 'Removed'),
)

BLURB_STATUS_CHOICES = (
    ('', 'N/A'),
    ('draft', 'Draft'),
    ('saved', 'Saved'),
    ('published', 'Published'),
    ('removed', 'Removed'),
)


class Song(models.Model):

    artist = models.CharField(max_length=256)
    title = models.CharField(max_length=400)

    # file will be uploaded to MEDIA_ROOT/somewhere
    mp3_file = models.FileField(upload_to='somewhere', null=True, blank=True)

    mp3_link = models.URLField(null=True, blank=True)
    youtube_link = models.URLField(null=True, blank=True)
    web_link = models.URLField(null=True, blank=True)

    image_url = models.URLField(null=True, blank=True)
    tagline = models.CharField(max_length=255, null=True, blank=True)

    wordpress_post_id = models.CharField(max_length=50, null=True, blank=True)
    display_user_ratings = models.BooleanField(default=True)
    status = models.CharField(choices=SONG_STATUS_CHOICES, max_length=20, default='open')

    publish_date = models.DateTimeField(help_text="Schedule a publish time here", null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    def saved_reviews(self):
        return self.review_set.filter(song=self, status__in=['saved', 'published'])

    @property
    def blurb_count(self):
        return self.saved_reviews().count()

    @property
    def css_class(self):
        if self.status == 'published':
            return 'dead'
        if self.blurb_count == 0:
            return 'new'
        elif self.blurb_count > 10:
            return 'closing'
        elif self.blurb_count > 5:
            return 'publish'
        return 'open'

    @property
    def closed(self):
        return True if self.status == 'published' else False

    def average_score(self):
        if self.blurb_count > 0:
            score_avg = self.saved_reviews().aggregate(models.Avg('score'))
            return round(score_avg.get('score__avg', 0), 2)
        return 0

    def controversy_index(self):
        """
        The basic formula is to take the difference between
        each score and the average score, add those all up, and then take the
        average of *that*. (The statistics name for this is "average deviation.")
        Then Dave uses a multiplier of .02 for every additional voter over eight, so
        if there are nine voters he multiplies by 1.02, if there are ten he
        multiplies by 1.04, eleven by 1.06, and so on.
        :return:
        """
        return 0

    def __str__(self):
        return "%s - %s" % (self.artist, self.title)

    class Meta:
        ordering = ['-upload_date']
        permissions = (
            ("can_edit_overall_score", "Editor can edit overall score"),
        )


class Review(models.Model):

    writer = models.ForeignKey(Writer)
    song = models.ForeignKey(Song)

    blurb = models.TextField(max_length=5000)
    score = models.IntegerField()

    sort_order = models.IntegerField(default=1)
    status = models.CharField(choices=BLURB_STATUS_CHOICES, max_length=20, default='draft')

    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s: %s" % (self.song.artist, self.song.title, self.writer.initials())

    class Meta:
        ordering = ['-create_date']
        permissions = (
            ("can_edit_blurb", "Editor can edit blurb"),
        )


class ScheduledWeek(models.Model):

    default_kwargs = {'limit_choices_to' : {'status': 'open'}, 'blank': True}

    monday = models.ManyToManyField(Song, related_name='mon_songs', **default_kwargs)
    tuesday = models.ManyToManyField(Song, related_name='tue_songs', **default_kwargs)
    wednesday = models.ManyToManyField(Song, related_name='wed_songs', **default_kwargs)
    thursday = models.ManyToManyField(Song, related_name='thu_songs', **default_kwargs)
    friday = models.ManyToManyField(Song, related_name='fri_songs', **default_kwargs)
    saturday = models.ManyToManyField(Song, related_name='sat_songs', **default_kwargs)
    sunday = models.ManyToManyField(Song, related_name='sun_songs', **default_kwargs)

    week_beginning = models.DateField()
    week_info = models.TextField(max_length=4000)
    current_week = models.BooleanField(help_text="Show as the current scheduled week", default=False)

    def __str__(self):
        return self.week_beginning.strftime("%D/%M/%Y")

    def weekdays(self):
        return [
            {'daystring': 'MONDAY', 'songs': self.monday.all()},
            {'daystring': 'TUESDAY', 'songs': self.tuesday.all()},
            {'daystring': 'WEDNESDAY', 'songs': self.wednesday.all()},
            {'daystring': 'THURSDAY', 'songs': self.thursday.all()},
            {'daystring': 'FRIDAY', 'songs': self.friday.all()},
            {'daystring': 'SATURDAY', 'songs': self.saturday.all()},
        ]

    class Meta:
        ordering = ['-week_beginning']
