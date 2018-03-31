from django.core.urlresolvers import reverse

from blurber.tests.test_models import SongTestBase


class HomePageTests(SongTestBase):
    def test_home_page_shows_most_recent_posts(self):
        resp = self.client.get(reverse('home_page'))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'home_page.html')
        self.assertQuerysetEqual(
            resp.context['recent_songs'],
            ['<Song: Brandy & Monica - The Boy Is Mine>']
        )
        self.assertEqual(resp.context['page_no'], 1)

    def test_home_page_paginates(self):
        resp = self.client.get(reverse('home_page') + '?paged=2')

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'home_page.html')
        self.assertEqual(resp.context['page_no'], 2)

    def test_home_page_ignores_invalid_pagination_param(self):
        resp = self.client.get(reverse('home_page') + '?paged=bananas')

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'home_page.html')
        self.assertEqual(resp.context['page_no'], 1)

    def test_home_page_with_post_id_param_redirects_to_single_post(self):
        resp = self.client.get(
            reverse('home_page') + '?p={}'.format(self.published_song.id),
            follow=True
        )

        self.assertEqual(resp.status_code, 200)
        self.assertRedirects(resp, reverse('single_post', kwargs={'song_id': self.published_song.id}))

    def test_home_page_ignores_non_int_post_id_param(self):
        resp = self.client.get(
            reverse('home_page') + '?p=bananas',
            follow=True
        )

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'home_page.html')

    def test_single_post_page_200s_for_published_songs(self):
        resp = self.client.get(reverse('single_post', kwargs={'song_id': self.published_song.id}))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'single_post.html')

    def test_single_post_page_404s_for_non_published_songs(self):
        for song in [self.song, self.new_song, self.closed_song]:
            resp = self.client.get(reverse('single_post', kwargs={'song_id': song.id}))
            self.assertEqual(resp.status_code, 404)

    def test_about_page_uses_template(self):
        resp = self.client.get(reverse('about'))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'about.html')


class SearchTests(SongTestBase):
    def test_search_results_get_redirects_to_home_page(self):
        resp = self.client.get(reverse('search'), follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'home_page.html')

    def test_search_results_post_shows_results(self):
        resp = self.client.post(reverse('search'), {'s': 'umbrella'})

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'search_results.html')
