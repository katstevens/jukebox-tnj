from datetime import datetime
from django.core.urlresolvers import reverse
from django.test import TestCase

from writers.models import Writer
from blurber.models import Song, Review, ScheduledWeek
from blurber.forms import ReviewForm


class BlurberViewTests(TestCase):

    def setUp(self):
        self.song = Song.objects.create(
            artist='2NE1',
            title='I Am The Best',
            status='open'
        )

        self.writer = self.generate_writer('readyforthisjelly@123.com')
        self.editor = self.generate_writer(
            'whenimoveyoumove@123.com',
            is_staff=True
        )

        self.saved_review = Review.objects.create(
            song=self.song,
            writer=self.writer,
            status='saved',
            score=5,
            blurb='Crowd say bo selecta'
        )

        self.week = ScheduledWeek.objects.create(
            week_beginning=datetime(2015,1,1),
            week_info='Let us get this party started.'
        )
        self.week.monday.add(self.song)

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

    def generate_new_song(self):
        return Song.objects.create(
            artist='Nicki Minaj',
            title='Beez in the Trap',
            status='open'
        )


class ScheduleViewTests(BlurberViewTests):

    def test_weekly_schedule_prompts_login_for_anon_user(self):

        resp = self.client.get(reverse('weekly_schedule'), follow=True)

        self.assertRedirects(resp, '/login/?next=%s' % reverse('weekly_schedule'))
        self.assertContains(resp, 'Please login to see this page.')

    def test_display_weekly_schedule_for_authenticated_writer(self):
        # Don't worry about how we're logged in for now
        r = self.client.force_login(self.writer)
        resp = self.client.get(reverse('weekly_schedule'), follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'schedule.html')

        # Check context
        self.assertEqual(resp.context['this_week'], self.week)
        self.assertQuerysetEqual(
            resp.context['all_open_songs'], ['<Song: 2NE1 - I Am The Best>']
        )
        self.assertEqual(resp.context['user_songs'], [self.song])

        # Should only be visible for staff
        self.assertNotContains(resp, 'Review all blurbs')

    def test_display_weekly_schedule_for_editor(self):

        r = self.client.force_login(self.editor)

        resp = self.client.get(reverse('weekly_schedule'))

        # Check context
        self.assertEqual(resp.context['this_week'], self.week)
        self.assertQuerysetEqual(
            resp.context['all_open_songs'], ['<Song: 2NE1 - I Am The Best>']
        )
        self.assertEqual(resp.context['user_songs'], [])

        # Should only be visible for staff
        self.assertContains(resp, 'Review all blurbs')


class WriteReviewViewTests(BlurberViewTests):

    def assert_response_content_for_new_song(self, resp, song, use_html=False):

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'write_blurb.html')

        # Check context
        self.assertIsInstance(resp.context['form'], ReviewForm)
        self.assertIsInstance(resp.context['form'].instance, Review)
        self.assertEqual(resp.context['song'], song)
        self.assertFalse(resp.context['preview_text'])

        if use_html:
            self.assertTrue(resp.context['use_html'])
            self.assertContains(resp, 'Edit with rich text editor.')
        else:
            self.assertFalse(resp.context['use_html'])
            self.assertContains(resp, 'Edit in plain-text editor to manually correct HTML.')

    def test_write_rich_text_review_for_new_song(self):
        r = self.client.force_login(self.writer)
        new_song = self.generate_new_song()
        self.assertEqual(new_song.blurb_count, 0)

        resp = self.client.get(
            reverse('write_review', kwargs={'song_id': new_song.id})
        )

        self.assert_response_content_for_new_song(resp, new_song)

        resp2 = self.client.post(
            reverse('write_review', kwargs={'song_id': new_song.id}),
            data={'blurb': 'Glowing appraisal', 'score': 10},
        )
        self.assertEqual(new_song.blurb_count, 1)

    def test_write_html_text_review_for_new_song(self):
        r = self.client.force_login(self.writer)
        new_song = self.generate_new_song()

        resp = self.client.get(
            reverse('write_review_html', kwargs={'song_id': new_song.id})
        )
        self.assert_response_content_for_new_song(resp, new_song, use_html=True)

    def assert_preview_text_shown(self, resp):
        # Check context
        self.assertTrue(resp.context['preview_text'])
        # Preview text
        self.assertContains(resp, 'Crowd say bo selecta<br /><strong>[5]</strong>')

    def assert_preview_text_not_shown(self, resp):
        # Preview text
        self.assertNotContains(resp, 'Crowd say bo selecta<br /><strong>[5]</strong>')

    def test_write_rich_text_review_for_existing_song(self):
        r = self.client.force_login(self.writer)

        resp = self.client.get(
            reverse('write_review', kwargs={'song_id': self.song.id})
        )
        self.assert_preview_text_shown(resp)

    def test_write_html_text_review_for_existing_song(self):
        r = self.client.force_login(self.writer)

        resp = self.client.get(
            reverse('write_review_html', kwargs={'song_id': self.song.id})
        )
        self.assert_preview_text_shown(resp)

    def test_submit_review_without_score_raises_form_error(self):
        r = self.client.force_login(self.writer)
        resp = self.client.post(
            reverse('write_review', kwargs={'song_id': self.song.id}),
            data={'blurb': 'Scathing dissection'}
        )
        self.assertFormError(resp, 'form', 'score', ['This field is required.'])
        self.assert_preview_text_not_shown(resp)

    def test_submit_review_without_blurb_raises_form_error(self):
        r = self.client.force_login(self.writer)
        resp = self.client.post(
            reverse('write_review', kwargs={'song_id': self.song.id}),
            data={'score': 0}
        )
        self.assertFormError(resp, 'form', 'blurb', ['This field is required.'])
        self.assert_preview_text_not_shown(resp)

    def test_submit_updated_review_and_continue_editing_shows_preview(self):
        r = self.client.force_login(self.writer)
        url = reverse('write_review', kwargs={'song_id': self.song.id})
        resp = self.client.post(
            url,
            data={'blurb': 'Scathing dissection', 'score': 0}
        )
        self.assertRedirects(resp, url)

    def test_submit_updated_review_and_return_to_schedule_does_redirect(self):
        r = self.client.force_login(self.writer)
        self.assertEqual(self.song.blurb_count, 1)

        resp = self.client.post(
            reverse('write_review', kwargs={'song_id': self.song.id}),
            data={
                'blurb': 'Scathing dissection',
                'score': 0,
                'submit_and_return_to_songlist': True
            },
            follow=True
        )
        self.assertRedirects(resp, reverse('weekly_schedule'))

        # We've just edited an existing review so the blurb count should
        # stay the same
        self.assertEqual(self.song.blurb_count, 1)
