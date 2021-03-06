from django.conf.urls import url

from writers.views import my_blurbs, writer_blurbs, all_writers

urlpatterns = [
    # The below are included under the /blurbs url space
    url(r'^$', my_blurbs, name='my_blurbs'),
    url(r'^(?P<status>\w+)/$', my_blurbs, name='my_blurbs_by_status'),
    url(r'^(?P<year>\d+)/$', my_blurbs, name='my_blurbs_by_year'),
    url(r'^(?P<year>\d+)/(?P<status>\w+)/$', my_blurbs, name='my_blurbs_by_year_and_status'),

    # Editors only
    url(r'^writers$', all_writers, name='all_writers'),
    url(r'^writers/sort/name/$', all_writers, {'order': 'name'}, name='all_writers_alphabetical'),
    url(r'^writer/(?P<writer_id>\d+)/$', writer_blurbs, name='writer_blurbs'),
    url(r'^writer/(?P<writer_id>\d+)/(?P<status>\w+)/$', writer_blurbs, name='writer_blurbs_by_status'),
    url(r'^writer/(?P<writer_id>\d+)/(?P<year>\d+)/$', writer_blurbs, name='writer_blurbs_by_year'),
    url(r'^writer/(?P<writer_id>\d+)/(?P<year>\d+)/(?P<status>\w+)/$', writer_blurbs, name='writer_blurbs_by_year_and_status'),

]