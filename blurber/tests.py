from django.test import TestCase

from writers.models import Writer
from blurber.models import Song, Review


class SongTests(TestCase):

    def setUp(self):
        self.song = Song.objects.create(
            artist='Roisín Murphy',
            title='Gone Fishing'
        )
        self.new_song = Song.objects.create(
            artist='Kate Bush',
            title='Washing Machine',
            status='new'
        )
        self.published_song = Song.objects.create(
            artist='Brandy & Monica',
            title='The Boy Is Mine',
            status='published'
        )

        self.writer = Writer.objects.create(
            username='readyforthisjelly@123.com',
            first_name='Michelle',
            last_name='Williams',
            email='readyforthisjelly@123.com'
        )

        self.saved_review = Review.objects.create(
            song=self.song,
            writer=self.writer,
            status='saved',
            score=5,
            blurb='Crowd say bo selecta'
        )

    def test_saved_reviews(self):

        self.assertQuerysetEqual(
            self.song.saved_reviews(),
            ['<Review: Roisín Murphy - Gone Fishing: MW>']
        )

    def test_blurb_count(self):

        self.assertEqual(self.song.blurb_count(), 1)

    def generate_additional_review(self, song, i):
        w = Writer.objects.create(
            username=i, email=i, first_name=i, last_name=i
        )
        next_review = Review(
            song=song,
            writer=w,
            blurb="blurb %s" % i,
            score=i,
            status='saved'
        )
        next_review.save()

    def test_css_class_for_blurb_ranges(self):

        # No blurbs
        self.assertEqual(self.new_song.css_class(), 'new')

        # Get first 5
        for i in range(0, 5):
            self.generate_additional_review(self.new_song, i)
            self.assertEqual(self.new_song.css_class(), 'open')

        # Get next 5
        for i in range(5, 10):
            self.generate_additional_review(self.new_song, i)
            self.assertEqual(self.new_song.css_class(), 'publish')

        # Add 1 more
        self.generate_additional_review(self.new_song, 10)
        self.assertEqual(self.new_song.css_class(), 'closing')

        # We should have 11 blurbs now
        self.assertEqual(self.new_song.blurb_count(), 11)

    def test_css_class_for_published_song_is_dead(self):

        self.assertTrue(self.published_song.css_class(), 'dead')

    def test_closed_is_false_for_open_status(self):

        self.assertFalse(self.song.closed())

    def test_closed_is_true_for_published_status(self):

        self.assertTrue(self.published_song.closed())

    def test_average_score_is_zero_for_zero_blurb_count(self):

        self.assertEqual(self.new_song.average_score(), 0)

    def test_average_score_for_3_blurbs(self):
        # Scores of 2, 7, 9 = average 18/3 = 6
        self.generate_additional_review(self.new_song, 2)
        self.generate_additional_review(self.new_song, 7)
        self.generate_additional_review(self.new_song, 9)

        self.assertEqual(self.new_song.average_score(), 6)

    def test_average_score_rounds_decimals_ok(self):
        # Scores of 1, 7, 9 = average 17/3 = 5.6666667
        self.generate_additional_review(self.new_song, 1)
        self.generate_additional_review(self.new_song, 7)
        self.generate_additional_review(self.new_song, 9)

        self.assertEqual(self.new_song.average_score(), 5.67)
