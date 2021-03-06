from datetime import datetime
from django.utils import timezone
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
            first_name="Michelle",
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
        self.published_review.create_date = datetime(2015, 2, 2, tzinfo=timezone.utc)
        self.published_review.save()

        self.saved_review = Review.objects.create(
            song=self.song2,
            writer=self.writer,
            score=10,
            blurb='BrillBuildingSkillz',
            status='saved'
        )
        self.saved_review.create_date = datetime(2015, 3, 3, tzinfo=timezone.utc)
        self.saved_review.save()

        self.week = ScheduledWeek.objects.create(
            week_beginning=datetime(2015,1,1, tzinfo=timezone.utc),
            week_info='Let us get this party started.'
        )
        self.week.monday.add(self.song1)

    def generate_writer(self, username, first_name="Robbie", is_staff=False):
        w = Writer.objects.create(
            username=username,
            first_name=first_name,
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

    def test_writer_lists_hidden_for_writer(self):
        self.assert_view_hidden_for_writer(reverse('all_writers'))
        self.assert_view_hidden_for_writer(reverse('all_writers_alphabetical'))

    def test_writer_list_by_most_recent_visible_for_editor(self):
        r = self.client.force_login(self.editor)
        resp = self.client.get(
            reverse('all_writers')
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed('all_writers.html')
        self.assertTrue(resp.context['editor_view'])

        # Writer Robbie has blurbed more recently than Editor Michelle
        self.assertEqual(self.writer, resp.context['writers'][0])
        self.assertEqual(self.editor, resp.context['writers'][1])

        self.assertTrue(resp.context['order_text'], "By Most Recent Blurb")
        self.assertContains(resp, "Sort alphabetically")

    def test_writer_list_by_name_visible_for_editor(self):
        r = self.client.force_login(self.editor)
        resp = self.client.get(
            reverse('all_writers_alphabetical')
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed('all_writers.html')
        self.assertTrue(resp.context['editor_view'])

        # Editor Michelle comes before Writer Robbie alphabetically
        self.assertEqual(self.editor, resp.context['writers'][0])
        self.assertEqual(self.writer, resp.context['writers'][1])

        self.assertTrue(resp.context['order_text'], "By Name")
        self.assertContains(resp, "Sort by most recently blurbed")

    def test_writer_with_no_blurbs_shows_empty_message_in_list(self):
        # Create a writer with no blurbs
        andy = self.generate_writer('amarillo@example.com', first_name="Andy")
        r = self.client.force_login(self.editor)
        resp = self.client.get(
            reverse('all_writers')
        )

        # Andy comes after Robbie and Michelle
        self.assertEqual(self.writer, resp.context['writers'][0])
        self.assertEqual(self.editor, resp.context['writers'][1])
        self.assertEqual(andy, resp.context['writers'][2])

        self.assertContains(resp, "Andy Williams")
        self.assertContains(resp, "No blurbs yet")


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
