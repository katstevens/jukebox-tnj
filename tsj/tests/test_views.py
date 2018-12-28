from django.core.urlresolvers import reverse

from writers.models import Writer
from blurber.tests.test_models import SongTestBase
from tsj.views import get_writers


class HomePageTests(SongTestBase):
    def test_home_page_shows_most_recent_posts(self):
        resp = self.client.get(reverse('home_page'))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'home_page.html')
        self.assertQuerysetEqual(
            resp.context['recent_songs'],
            ['<PublicPost: Brandy & Monica - The Boy Is Mine>']
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
            reverse('home_page') + '?p={}'.format(self.public_post.id),
            follow=True
        )

        self.assertEqual(resp.status_code, 200)
        self.assertRedirects(resp, reverse('single_post', kwargs={'song_id': self.public_post.id}))

    def test_home_page_ignores_non_int_post_id_param(self):
        resp = self.client.get(
            reverse('home_page') + '?p=bananas',
            follow=True
        )

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'home_page.html')

    def test_single_post_page_200s_for_published_songs(self):
        resp = self.client.get(reverse('single_post', kwargs={'song_id': self.public_post.id}))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'single_post.html')

    def test_about_page_uses_template(self):
        resp = self.client.get(reverse('about'))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'about.html')

    def test_get_writers_shows_active_public_writers_sorted_by_last_name(self):
        w2 = Writer(username='2', first_name='Nichelle', last_name='Williams', email='nichell@example.com')
        w2.save()
        w3 = Writer(username='3', first_name='Dooby', last_name='Duck', email='dooby@example.com', is_active=False)
        w3.save()
        w4 = Writer(username='4', first_name='DLacey', last_name='Hideaway', email='dlacey@example.com', public=False)
        w4.save()
        w5 = Writer(username='5', first_name='Michelle G.', last_name='Williams', email='ma@example.com')
        w5.save()
        self.assertQuerysetEqual(
            get_writers(),
            ['<Writer: Michelle Williams>', '<Writer: Michelle G. Williams>', '<Writer: Nichelle Williams>']
        )

    def test_search_results_get_with_param_shows_results(self):
        resp = self.client.get(reverse('home_page') + '?s=boy')

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'search_results.html')
