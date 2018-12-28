from datetime import datetime, timezone
from django.test import TestCase

from writers.models import Writer
from tsj.models import PublicPost
from blurber.models import Song, Review, ScheduledWeek


class SongTestBase(TestCase):

    def setUp(self):
        self.song = Song.objects.create(
            artist='Roisín Murphy',
            title='Gone Fishing'
        )
        self.new_song = Song.objects.create(
            artist='Kate Bush',
            title='Washing Machine',
            status='open'
        )
        self.published_song = Song.objects.create(
            artist='Brandy & Monica',
            title='The Boy Is Mine',
            status='published'
        )
        self.closed_song = Song.objects.create(
            artist='Girls Aloud',
            title='The Promise',
            status='closed'
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
        self.public_post = PublicPost.objects.create(
            song=self.published_song,
            html_content="Brandy & Monica - The Boy Is Mine, some more content",
            published_on=datetime(2018, 12, 1, tzinfo=timezone.utc)
        )

    @staticmethod
    def generate_additional_review(song, i, score=None, status='saved'):
        if not score:
            score = i
        w = Writer.objects.create(
            username=i, email=i, first_name=i, last_name=i
        )
        next_review = Review(
            song=song,
            writer=w,
            blurb="blurb %s" % i,
            score=score,
            status=status,
            sort_order=i
        )
        next_review.save()
        return next_review


class SongTests(SongTestBase):
    def test_saved_reviews(self):

        self.assertQuerysetEqual(
            self.song.saved_reviews(),
            ['<Review: Roisín Murphy - Gone Fishing: MW>']
        )

    def test_published_reviews_uses_sort_order(self):
        r = self.generate_additional_review(self.published_song, 2, status='published')
        r = self.generate_additional_review(self.published_song, 1, status='published')
        # TODO: all reviews should have their status changed when song is published
        r = self.generate_additional_review(self.published_song, 3, status='saved')
        self.assertQuerysetEqual(
            self.published_song.published_reviews(),
            [
                '<Review: Brandy & Monica - The Boy Is Mine: 11>',
                '<Review: Brandy & Monica - The Boy Is Mine: 22>'
            ]
        )

    def test_blurb_count(self):

        self.assertEqual(self.song.blurb_count, 1)

    def test_css_class_for_blurb_ranges(self):

        # No blurbs
        self.assertEqual(self.new_song.css_class, 'new')

        # Get first 5
        for i in range(0, 5):
            self.generate_additional_review(self.new_song, i)
            self.assertEqual(self.new_song.css_class, 'open')

        # Get next 5
        for i in range(5, 10):
            self.generate_additional_review(self.new_song, i)
            self.assertEqual(self.new_song.css_class, 'publish')

        # Add 1 more
        self.generate_additional_review(self.new_song, 10)
        self.assertEqual(self.new_song.css_class, 'closing')

        # We should have 11 blurbs now
        self.assertEqual(self.new_song.blurb_count, 11)

    def test_css_class_for_published_song_is_dead(self):

        self.assertEqual(self.published_song.css_class, 'dead')
        self.assertEqual(self.closed_song.css_class, 'dead')

    def test_closed_is_false_for_open_status(self):

        self.assertFalse(self.song.closed)

    def test_closed_is_true_for_published_status(self):

        self.assertTrue(self.published_song.closed)
        self.assertTrue(self.closed_song.closed)

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

    def test_search_reviews_in_admin(self):
        self.assertEqual(
            self.new_song.admin_review_search_link,
            "<a href='/admin/blurber/review/?q=washing+machine'>"
            "Search for reviews of this song</a>"
        )

class ControversyIndexTests(SongTestBase):

    def test_multiplier_for_8_reviews_is_exactly_1(self):
        for i in range(7):
            self.generate_additional_review(self.song, i)

        self.assertEqual(self.song.multiplier, 1)

    def test_multiplier_for_over_9_reviews_increases(self):
        """
        Use a multiplier of .02 for every additional voter over eight, so
        if there are nine voters, multiply by 1.02, if there are ten,
        multiply by 1.04, eleven by 1.06, and so on.
        """
        mult = 1
        for i in range(7):
            self.generate_additional_review(self.song, i)
            self.assertEqual(self.song.multiplier, mult)

        for i in range(3):
            self.generate_additional_review(self.song, i+7)
            mult += 0.02
            self.assertEqual(self.song.multiplier, mult)

    def test_controversy_index_for_8_songs(self):
        """
        # Scores of 0, 1, 2, 3, 4, 5, 5, 6
        # Average score is 3.25
        # Total deviation: 3.25+2.25+1.25+0.25+0.75+1.75+1.75+2.75 = 14
        # Average deviation 14/8 = 1.75
        """
        for i in range(7):
            self.generate_additional_review(self.song, i)

        self.assertEqual(self.song.blurb_count, 8)
        self.assertEqual(self.song.average_score(), 3.25)
        self.assertEqual(
            self.song.controversy_index(), 1.75
        )

    def test_controversy_index_for_0_reviews_is_0(self):
        song = Song.objects.create(
            artist='Gang of Four',
            title='What We All Want',
            status='published'
        )
        self.assertEqual(song.blurb_count, 0)
        self.assertEqual(song.controversy_index(), 0)

    def test_controversy_index_for_equal_scoring_reviews_is_0(self):
        song = Song.objects.create(
            artist='Gang of Four',
            title='I Love A Man In Uniform',
            status='published'
        )
        for i in range(5):
            self.generate_additional_review(song, i, score=3)

        self.assertEqual(song.blurb_count, 5)
        self.assertEqual(song.controversy_index(), 0)

    def test_controversy_debug_string(self):
        song = Song.objects.create(
            artist='Gang of Four',
            title="Natural's Not In It",
            status='published'
        )
        for i in range(5):
            self.generate_additional_review(song, i)

        self.assertEqual(
            song.controversy_debug_string(),
            "[1.2][1][5]"
        )


class ScheduledWeekTests(TestCase):

    def setUp(self):
        self.new_song = Song.objects.create(
            artist='Sisquo',
            title='Thong Song',
            status='new'
        )
        self.another_song = Song.objects.create(
            artist='Prince',
            title='1999',
            status='new'
        )
        self.yet_another_song = Song.objects.create(
            artist='UB40',
            title='Rat In My Kitchen',
            status='new'
        )

    def test_week_summary_shows_all(self):
        s = ScheduledWeek.objects.create(
            week_beginning=datetime(2015, 1, 1),
        )
        for day in s._all_days():
            day.add(self.new_song)

        actual = s.week_summary
        self.assertEqual(
            actual, "Sisquo, Sisquo, Sisquo, Sisquo, Sisquo, Sisquo"
        )

    def test_week_summary_shows_truncated(self):
        s = ScheduledWeek.objects.create(
            week_beginning=datetime(2015, 1, 1),
        )
        for day in s._all_days():
            day.add(self.new_song)
            day.add(self.another_song)
            day.add(self.yet_another_song)

        actual = s.week_summary
        expected = "UB40, Prince, Sisquo, UB40, Prince, Sisquo, UB40, Prince, Sisquo, " \
                   "UB40, Prince, Sisquo, UB40, Prince, Sisquo, UB40, Prince, Sisq..."
        self.assertEqual(
            actual, expected
        )

    def test_weekdays(self):
        s = ScheduledWeek.objects.create(
            week_beginning=datetime(2015, 1, 1, tzinfo=timezone.utc),
        )
        s.monday.add(self.new_song)

        actual = s.weekdays()

        self.assertQuerysetEqual(
            actual[0]['songs'],
            ['<Song: Sisquo - Thong Song>']
        )
        for i in range(1, 5):
            self.assertQuerysetEqual(actual[i]['songs'], [])
