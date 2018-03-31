from unittest.mock import patch, call, Mock

from datetime import datetime
from django.core.urlresolvers import reverse
from django.test import TestCase

from writers.models import Writer
from blurber.models import Song, Review, ScheduledWeek
from blurber.forms import ReviewForm, UploadSongForm


class BlurberBaseViewTests(TestCase):

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

    def generate_new_song(self, status='open'):
        return Song.objects.create(
            artist='Nicki Minaj',
            title='Beez in the Trap',
            status=status
        )

    def assert_view_hidden_for_writer(self, url):
        r = self.client.force_login(self.writer)
        resp = self.client.get(url, follow=True)

        self.assertRedirects(resp, '/login/?next=%s' % url)
        self.assertContains(resp, "Your account doesn't have access to this page.")


class ScheduleViewTests(BlurberBaseViewTests):

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
        self.assertContains(
            resp, reverse('admin:blurber_song_change', args=[self.song.id])
        )


class WriteReviewViewTests(BlurberBaseViewTests):

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


class UploadSongTests(BlurberBaseViewTests):

    def test_upload_song_form_hidden_for_writer(self):
        self.assert_view_hidden_for_writer(reverse('upload_song'))

    def test_upload_song_form_displays_for_editor(self):
        r = self.client.force_login(self.editor)

        resp = self.client.get(reverse('upload_song'))

        self.assertTemplateUsed(resp, 'upload_song.html')
        self.assertIsInstance(resp.context['form'], UploadSongForm)
        self.assertFalse(resp.context['song'])

    def test_upload_song_with_missing_title_raises_form_error(self):
        r = self.client.force_login(self.editor)

        resp = self.client.post(
            reverse('upload_song'),
            data={'artist': 'Roxy Music'}
        )
        self.assertFormError(resp, 'form', 'title', ['This field is required.'])

    def test_upload_song_with_missing_artist_raises_form_error(self):
        r = self.client.force_login(self.editor)

        resp = self.client.post(
            reverse('upload_song'),
            data={'title': 'Love Is 1x Drug'}
        )
        self.assertFormError(resp, 'form', 'artist', ['This field is required.'])

    def test_upload_song_with_bad_url_raises_form_error(self):
        r = self.client.force_login(self.editor)

        resp = self.client.post(
            reverse('upload_song'),
            data={
                'artist': 'Roxy Music',
                'title': 'Love Is 1x Drug',
                'mp3_link': 'Pret Sandwiches'
            }
        )
        self.assertFormError(resp, 'form', 'mp3_link', ['Enter a valid URL.'])

    def test_submit_upload_song_form_and_continue_uploading_shows_new_form(self):
        r = self.client.force_login(self.editor)

        resp = self.client.post(
            reverse('upload_song'),
            data={
                'artist': 'Roxy Music',
                'title': 'Love Is 1x Drug',
                'mp3_link': 'http://123.com'
            }
        )
        # Song should be saved
        newly_uploaded_song = Song.objects.filter(title='Love Is 1x Drug')
        self.assertEqual(newly_uploaded_song.count(), 1)
        self.assertEqual(resp.context['song'], newly_uploaded_song[0])

        # Success message displayed
        self.assertContains(resp, '<em>Roxy Music - Love Is 1x Drug</em> successfully uploaded.')
        # Blank form displayed
        self.assertEqual(resp.context['form']['artist'].value(), None)

    def test_submit_upload_song_form_and_return_to_schedule_does_redirect(self):
        r = self.client.force_login(self.editor)

        resp = self.client.post(
            reverse('upload_song'),
            data={
                'artist': 'Buzzcocks',
                'title': 'Boredom',
                'mp3_link': 'http://123.com',
                'submit_and_return_to_songlist': True
            },
            follow=True
        )
        # Song should be saved
        newly_uploaded_song = Song.objects.filter(title='Boredom')
        self.assertEqual(newly_uploaded_song.count(), 1)

        self.assertRedirects(resp, reverse('weekly_schedule'))
        # New song should be shown in the list
        self.assertContains(resp, '<strong>Buzzcocks</strong> - Boredom')


class ViewReviewsTest(BlurberBaseViewTests):

    def test_review_list_hidden_for_writer(self):
        url = reverse('view_reviews', kwargs={'song_id': self.song.id })
        self.assert_view_hidden_for_writer(url)

    def test_review_list_displays_for_editor(self):
        r = self.client.force_login(self.editor)
        url = reverse('view_reviews', kwargs={'song_id': self.song.id })
        resp = self.client.get(url)

        self.assertTemplateUsed(resp, 'view_reviews.html')
        self.assertQuerysetEqual(resp.context['reviews'], ['<Review: 2NE1 - I Am The Best: MW>'])
        self.assertEqual(resp.context['song'], self.song)
        self.assertEqual(resp.context['review_count'], 1)
        self.assertContains(
            resp, reverse('admin:blurber_song_change', args=[self.song.id])
        )

    def test_close_link_shown_if_song_open(self):
        self.client.force_login(self.editor)
        resp = self.client.get(reverse('view_reviews', kwargs={'song_id': self.song.id}))

        self.assertContains(
            resp, reverse('close_song', args=[self.song.id])
        )
        self.assertNotContains(
            resp, reverse('preview_post', args=[self.song.id])
        )

    def test_preview_link_shown_if_song_already_closed(self):
        self.client.force_login(self.editor)
        closed_song = self.generate_new_song(status='closed')
        resp = self.client.get(reverse('view_reviews', kwargs={'song_id': closed_song.id}))

        self.assertContains(
            resp, reverse('preview_post', args=[closed_song.id])
        )
        self.assertNotContains(
            resp, reverse('close_song', args=[closed_song.id])
        )

    def assert_review_moved_to_position(self, url, expected_position):

        for i in range(3):
            Review.objects.create(
                song=self.song,
                writer=self.generate_writer('writer%s@place%s.com' % (i, i)),
                blurb='Somewhat repetitive',
                status='saved',
                score=i,
                sort_order=i+1
            )

        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['review_count'], 4)

        # Review should be sorted in consecutive ascending order
        self.assertQuerysetEqual(
            resp.context['reviews'].values_list('sort_order', flat=True),
            ['1', '2', '3', '4'],
        )
        # Check our saved review is in expected position
        self.assertEqual(
            resp.context['reviews'][expected_position].id,
            self.saved_review.id
        )

    def test_move_existing_top_review_to_top(self):
        r = self.client.force_login(self.editor)
        url = reverse('move_review_top', kwargs={'review_id': self.saved_review.id})

        # Should be 1/4 in queryset
        self.assert_review_moved_to_position(url, 0)

    def test_move_non_top_review_to_top(self):
        r = self.client.force_login(self.editor)
        # Put sort order as something wacky
        self.saved_review.sort_order = 8
        self.saved_review.save()
        url = reverse('move_review_top', kwargs={'review_id': self.saved_review.id})

        # Should be 1/4 in queryset
        self.assert_review_moved_to_position(url, 0)

    def test_move_existing_bottom_review_to_bottom(self):
        r = self.client.force_login(self.editor)
        self.saved_review.sort_order = 8
        self.saved_review.save()
        url = reverse('move_review_bottom', kwargs={'review_id': self.saved_review.id})

        # Should be 1/4 in queryset
        self.assert_review_moved_to_position(url, 3)

    def test_move_non_bottom_review_to_bottom(self):
        r = self.client.force_login(self.editor)
        self.saved_review.sort_order = 1
        self.saved_review.save()
        url = reverse('move_review_bottom', kwargs={'review_id': self.saved_review.id})

        # Should be 1/4 in queryset
        self.assert_review_moved_to_position(url, 3)

    def test_move_non_top_review_up_one_spot(self):
        r = self.client.force_login(self.editor)
        self.saved_review.sort_order = 8
        self.saved_review.save()
        url = reverse('move_review_up', kwargs={'review_id': self.saved_review.id})

        # Should be 3/4 in queryset
        self.assert_review_moved_to_position(url, 2)

    def test_move_top_review_up_one_spot(self):
        r = self.client.force_login(self.editor)
        url = reverse('move_review_up', kwargs={'review_id': self.saved_review.id})

        # Should still be 1/4 in queryset
        self.assert_review_moved_to_position(url, 0)

    def test_move_bottom_review_down_one_spot(self):
        r = self.client.force_login(self.editor)
        self.saved_review.sort_order = 8
        self.saved_review.save()
        url = reverse('move_review_down', kwargs={'review_id': self.saved_review.id})

        # Should be 4/4 in queryset
        self.assert_review_moved_to_position(url, 3)

    def test_move_non_bottom_review_down_one_spot(self):
        r = self.client.force_login(self.editor)
        self.saved_review.sort_order = 2
        self.saved_review.save()
        url = reverse('move_review_down', kwargs={'review_id': self.saved_review.id})

        # Should be 3/4 in queryset
        self.assert_review_moved_to_position(url, 2)


class PreviewPostTests(BlurberBaseViewTests):

    def test_preview_post_hidden_for_writer(self):
        url = reverse('preview_post', kwargs={'song_id': self.song.id })
        self.assert_view_hidden_for_writer(url)

    def test_preview_post_displays_for_editor(self):
        r = self.client.force_login(self.editor)
        url = reverse('preview_post', kwargs={'song_id': self.song.id })
        resp = self.client.get(url)

        self.assertTemplateUsed(resp, 'preview_post.html')
        self.assertQuerysetEqual(resp.context['reviews'], ['<Review: 2NE1 - I Am The Best: MW>'])
        self.assertEqual(resp.context['song'], self.song)
        self.assertTrue(resp.context['show_admin_links'])
        self.assertContains(resp, "Preview")
        self.assertContains(resp, self.song.controversy_debug_string())
        self.assertContains(
            resp, reverse('admin:blurber_song_change', args=[self.song.id])
        )

    def test_fetch_html_hidden_for_writer(self):
        url = reverse('fetch_html', kwargs={'song_id': self.song.id })
        self.assert_view_hidden_for_writer(url)

    def test_fetch_html_displays_for_editor(self):
        r = self.client.force_login(self.editor)
        url = reverse('fetch_html', kwargs={'song_id': self.song.id })
        resp = self.client.get(url)

        self.assertTemplateUsed(resp, 'preview_source.html')
        self.assertQuerysetEqual(resp.context['reviews'], ['<Review: 2NE1 - I Am The Best: MW>'])
        self.assertEqual(resp.context['song'], self.song)
        self.assertFalse(resp.context['show_admin_links'])
        self.assertNotContains(resp, "Preview")
        self.assertNotContains(resp, self.song.controversy_debug_string())


class PublishPostTests(BlurberBaseViewTests):

    @patch('blurber.views._song_html_content')
    @patch('blurber.views._create_wp_post')
    @patch('blurber.views._post_to_wp')
    def test_publish_post_calls_rpc_client(self, myclient, mypost, mycontent):
        myclient.return_value = "TESTID"
        mycontent.return_value = Mock(content="<h1>Testing</h1>")

        r = self.client.force_login(self.editor)
        url = reverse('publish_song_to_wordpress', kwargs={'song_id': self.song.id})
        resp = self.client.get(url)

        # The mocked functions should be called correctly
        self.assertEqual(
            mypost.call_args, call(self.song, "&lt;h1&gt;Testing&lt;/h1&gt;")
        )
        self.assertEqual(
            myclient.call_args, call(mypost.return_value)
        )
        # The view should give a success message
        self.assertEqual(resp.content, b"Song posted successfully - Wordpress ID TESTID")
        # The wordpress ID should be saved
        updated_song = Song.objects.get(id=self.song.id)
        self.assertEqual(updated_song.wordpress_post_id, 'TESTID')
