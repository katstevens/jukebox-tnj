from datetime import datetime, timezone
from django.test import TestCase
from tsj.models import PublicPost, Song


class PublicPostTest(TestCase):

    def test_can_create_public_post_and_search_for_it_later(self):
        song = Song.objects.create(
            artist='Kate Bush',
            title='Washing Machine',
            status='open'
        )
        pp = PublicPost.objects.create(
            html_content="<h2>Title</h2><p>Body</p>",
            song=song,
            published_on=datetime.utcnow()
        )
        pp.save()

        results = PublicPost.objects.filter(html_content__icontains="body")

        assert str(results[0]) == "Kate Bush - Washing Machine"
        assert results[0].html_content == "<h2>Title</h2><p>Body</p>"
