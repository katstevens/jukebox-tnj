from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse

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

    status = models.CharField(choices=SONG_STATUS_CHOICES, max_length=20, default='open',
                              help_text="Close/publish/remove the song here.")

    # file will be uploaded to MEDIA_ROOT/somewhere
    mp3_file = models.FileField(upload_to='somewhere', null=True, blank=True,
                                help_text="Will be available to writers in the blurber only.")

    mp3_link = models.URLField(null=True, blank=True,
                               help_text="Will be available to writers in the blurber only.")
    youtube_link = models.URLField(null=True, blank=True,
                                   help_text="Will be available to writers in the blurber AND"
                                             " on published post.")
    web_link = models.URLField(null=True, blank=True,
                               help_text="Will appear on published post")

    image_url = models.URLField(null=True, blank=True,
                                help_text="Will appear on published post.")
    tagline = models.CharField(max_length=255, null=True, blank=True,
                               help_text="Will appear on published post.")

    wordpress_post_id = models.CharField(max_length=50, null=True, blank=True,
                                         help_text="Auto-filled on publish.")
    display_user_ratings = models.BooleanField(default=True,
                                               help_text="I don't know what this does"
                                                         " but prob something to do with Wordpress")

    publish_date = models.DateTimeField(help_text="Schedule a publish time here (TODO)", null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    def saved_reviews(self):
        return self.review_set.filter(song=self, status__in=['saved', 'published'])

    @property
    def blurb_count(self):
        return self.saved_reviews().count()

    @property
    def css_class(self):
        if self.status in ['published', 'closed']:
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
        return True if self.status in ['published', 'closed'] else False

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
        """
        avg_score = self.average_score()
        review_count = self.blurb_count
        # Return zero for a song with no reviews.
        if review_count < 1:
            return 0

        running_deviation = 0
        for bl in self.saved_reviews():
            running_deviation += abs(avg_score - bl.score)
        avg_deviation = running_deviation / review_count

        return self.multiplier * avg_deviation

    @property
    def multiplier(self):
        if self.blurb_count < 9:
            extra_weighting = 0
        else:
            extra_weighting = (self.blurb_count-8)*0.02
        return 1 + extra_weighting

    def controversy_debug_string(self):
        return "[%s][%s][%s]" % (self.controversy_index(), self.multiplier, self.blurb_count)

    @property
    def admin_review_search_link(self):
        base_url = reverse('admin:blurber_song_changelist')
        query_string = self.title.lower().replace(' ', '+')
        return "<a href='%s?q=%s'>Search for reviews of this song</a>" % (base_url, query_string)

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
    blurb_backup = models.TextField(max_length=5000, blank=True, null=True)
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

    def _all_days(self):
        return [
            self.monday,
            self.tuesday,
            self.wednesday,
            self.thursday,
            self.friday,
            self.saturday
        ]

    # For display in admin
    def day_summary(self, day):
        return "\n".join(day.values_list('artist', flat=True))

    @property
    def monday_songs(self):
        return self.day_summary(self.monday.all())
    @property
    def tuesday_songs(self):
        return self.day_summary(self.tuesday.all())
    @property
    def wednesday_songs(self):
        return self.day_summary(self.wednesday.all())
    @property
    def thursday_songs(self):
        return self.day_summary(self.thursday.all())
    @property
    def friday_songs(self):
        return self.day_summary(self.friday.all())
    @property
    def saturday_songs(self):
        return self.day_summary(self.saturday.all())

    @property
    def week_summary(self):
        summary = ", ".join(
            [", ".join(day.all().values_list('artist', flat=True)) for day in self._all_days()]
        )
        if len(summary) > 128:
            return summary[:128] + "..."
        return summary

    class Meta:
        ordering = ['-week_beginning']
