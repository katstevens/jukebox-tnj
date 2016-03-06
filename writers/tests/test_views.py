from datetime import datetime
from django.core.urlresolvers import reverse
from django.test import TestCase

from unittest.mock import patch

from writers.models import Writer
from blurber.models import Song, Review, ScheduledWeek


class WriterBaseViewTests(TestCase):

    def setUp(self):

        self.writer = self.generate_writer('readyforthisjelly@123.com')
        self.editor = self.generate_writer(
            'whenimoveyoumove@123.com',
            is_staff=True
        )

        self.song1 = Song.objects.create(
            artist='Kendrick Lemar',
            title='King Kunta',
            status='published'
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
        )
        self.published_review.create_date = datetime(2015, 2, 2)
        self.published_review.save()

        self.saved_review = Review.objects.create(
            song=self.song2,
            writer=self.writer,
            score=10,
            blurb='BrillBuildingSkillz',
            status='saved',
            create_date=datetime(2015,3,3)
        )
        self.saved_review.create_date = datetime(2015, 3, 3)
        self.saved_review.save()

        self.week = ScheduledWeek.objects.create(
            week_beginning=datetime(2015,1,1),
            week_info='Let us get this party started.'
        )
        self.week.monday.add(self.song1)

    def generate_writer(self, username, is_staff=False):
        w = Writer.objects.create(
            username=username,
            first_name='Michelle',
            last_name='Williams',
            email=username,
            is_staff=is_staff
        )
        w.set_password('test1234')
        w.save()
        return w

    def assert_view_hidden_for_writer(self, url):
        r = self.client.force_login(self.writer)
        resp = self.client.get(url, follow=True)

        self.assertRedirects(resp, '/login/?next=%s' % url)
        self.assertContains(resp, "Your account doesn't have access to this page.")


@patch('writers.views.CURRENT_YEAR', 2015)
class WriterViewTests(WriterBaseViewTests):

    def test_my_blurbs_redirects_for_anon_user(self):
        resp = self.client.get(reverse('my_blurbs'), follow=True)
        self.assertRedirects(resp, '/login/?next=%s' % reverse('my_blurbs'))
        self.assertContains(resp, 'Please login to see this page.')

    def test_my_blurbs_defaults_to_current_year(self):

        r = self.client.force_login(self.writer)
        resp = self.client.get(reverse('my_blurbs'))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'my_blurbs.html')
        self.assertEqual(
            set([self.published_review, self.saved_review]),
            set(resp.context['reviews'])
        )
        self.assertEqual(resp.context['year'], 2015)
        self.assertFalse(resp.context['editor_view'])

    def test_my_blurbs_published_only(self):
        r = self.client.force_login(self.writer)
        resp = self.client.get(
            reverse('my_blurbs_by_status', kwargs={'status': 'published'})
        )

        self.assertEqual(
            set([self.published_review]),
            set(resp.context['reviews'])
        )

    def test_my_blurbs_pending_only(self):
        r = self.client.force_login(self.writer)
        resp = self.client.get(
            reverse('my_blurbs_by_status', kwargs={'status': 'saved'})
        )

        self.assertEqual(
            set([self.saved_review]),
            set(resp.context['reviews'])
        )

    # TODO: Test coverage for blurbs listed by year

    def test_writer_blurbs_hidden_for_writer(self):
        # Either for the writer themselves, or any other writer
        self.assert_view_hidden_for_writer(
            reverse('writer_blurbs', kwargs={'writer_id': self.writer.id})
        )
        another_writer = self.generate_writer('a@b.com')
        self.assert_view_hidden_for_writer(
            reverse('writer_blurbs', kwargs={'writer_id': another_writer.id})
        )

    def test_writer_blurbs_visible_for_editor(self):
        r = self.client.force_login(self.editor)
        resp = self.client.get(
            reverse('writer_blurbs', kwargs={'writer_id': self.writer.id})
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed('my_blurbs.html')
        self.assertIn(self.published_review, resp.context['reviews'])
        self.assertEqual(
            set([self.published_review, self.saved_review]),
            set(resp.context['reviews'])
        )
        self.assertTrue(resp.context['editor_view'])


class RegistrationTests(WriterBaseViewTests):

    def test_login_page_shows_template_and_default_redirects_to_schedule(self):

        resp = self.client.get(reverse('login'))
        self.assertTemplateUsed('registration/login.html')
        self.assertEqual(resp.status_code, 200)

        resp2 = self.client.post(
            reverse('login'),
            {'username': self.writer.username, 'password': 'test1234'},
            follow=True
        )

        self.assertRedirects(resp2, reverse('weekly_schedule'))

    def test_login_with_next_goes_to_that_url(self):

        resp = self.client.post(
            reverse('login') + '?next=' + reverse('my_blurbs'),
            {'username': self.writer.username, 'password': 'test1234'},
            follow=True
        )
        self.assertRedirects(resp, reverse('my_blurbs'))
