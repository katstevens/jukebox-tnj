from datetime import datetime
from django.core.urlresolvers import reverse
from django.test import TestCase

from writers.models import Writer
from blurber.models import Song, Review


class WriterViewTests(TestCase):

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
            status='published'
        )
        self.saved_review = Review.objects.create(
            song=self.song2,
            writer=self.writer,
            score=10,
            blurb='BrillBuildingSkillz',
            status='saved'
        )

    def test_my_blurbs_redirects_for_anon_user(self):
        resp = self.client.get(reverse('my_blurbs'), follow=True)
        self.assertRedirects(resp, '/login/?next=%s' % reverse('my_blurbs'))
        self.assertContains(resp, 'Please login to see this page.')

    def test_my_blurbs_defaults_to_current_year(self):

        r = self.client.force_login(self.writer)
        resp = self.client.get(reverse('my_blurbs'), follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'my_blurbs.html')