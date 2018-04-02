from datetime import datetime
from django.test import TestCase
from django.utils import timezone

from writers.models import Writer
from blurber.models import Song, Review


class WriterTests(TestCase):

    def setUp(self):

        self.writer = Writer.objects.create(
            username='abc@123.com',
            first_name='Kelly',
            last_name='Rowland',
            email='abc@123.com'
        )

        self.song1 = Song.objects.create(
            artist='Kendrick Lemar',
            title='King Kunta'
        )
        self.song2 = Song.objects.create(
            artist='Kendrick Lemar',
            title='Swimming Pools (Drank)'
        )
        self.published_review = Review.objects.create(
            song=self.song1,
            writer=self.writer,
            score=10,
            blurb='BrillSkillz',
            status='published',
            create_date=datetime(2016, 1, 1, tzinfo=timezone.utc)
        )
        self.saved_review = Review.objects.create(
            song=self.song2,
            writer=self.writer,
            score=10,
            blurb='BrillBuildingSkillz',
            status='saved'
        )
        self.published_review.create_date = datetime(2016, 1, 1, tzinfo=timezone.utc)
        self.published_review.save()
        self.saved_review.create_date = datetime(2016, 1, 7, tzinfo=timezone.utc)
        self.saved_review.save()

    def test_published_blurb_history(self):

        self.assertQuerysetEqual(
            self.writer.published_blurb_history(),
            ['<Review: Kendrick Lemar - King Kunta: KR>']
        )

    def test_initials(self):

        self.assertEqual(self.writer.initials(), "KR")

    def test_bio_link_display_defaults_to_search(self):
        self.assertEqual(self.writer.bio_link_display(), "?s=kelly+rowland")

    def test_bio_link_display_incorporats_field(self):
        self.writer.bio_link = 'http://example.com'
        self.writer.save()
        self.assertEqual(self.writer.bio_link_display(), "http://example.com")

    def test_bio_name(self):
        self.assertEqual(self.writer.bio_name(), "Rowland, K.")

    def test_get_full_name(self):

        self.assertEqual(self.writer.get_full_name(), "Kelly Rowland")

    def test_get_short_name(self):

        self.assertEqual(self.writer.get_short_name(), "Kelly Rowland")

    def test_blurb_history_is_sorted_most_recent_first(self):

        self.assertQuerysetEqual(
            self.writer.blurb_history(),
            ['<Review: Kendrick Lemar - Swimming Pools (Drank): KR>',
             '<Review: Kendrick Lemar - King Kunta: KR>']
        )

    def test_last_blurb_date_picks_right_date(self):

        self.assertEqual(
            self.writer.last_blurb_date(),
            datetime(2016, 1, 7, tzinfo=timezone.utc)
        )
