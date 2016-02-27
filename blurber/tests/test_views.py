from datetime import datetime
from django.core.urlresolvers import reverse
from django.test import TestCase

from writers.models import Writer
from blurber.models import Song, Review, ScheduledWeek


class ScheduleViewTests(TestCase):

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

        resp = self.client.get(reverse('weekly_schedule'), follow=True)

        # Check context
        self.assertEqual(resp.context['this_week'], self.week)
        self.assertQuerysetEqual(
            resp.context['all_open_songs'], ['<Song: 2NE1 - I Am The Best>']
        )
        self.assertEqual(resp.context['user_songs'], [])

        # Should only be visible for staff
        self.assertContains(resp, 'Review all blurbs')
