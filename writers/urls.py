from django.conf.urls import url

from writers.views import my_blurbs, writer_blurbs

urlpatterns = [
    # The below are included under the /myblurbs url space
    url(r'^$', my_blurbs, name='my_blurbs'),
    url(r'^(?P<status>\w+)/$', my_blurbs, name='my_blurbs_by_status'),
    url(r'^(?P<year>\d+)/$', my_blurbs, name='my_blurbs_by_year'),
    url(r'^(?P<year>\d+)/(?P<status>\w+)/$', my_blurbs, name='my_blurbs_by_year_and_status'),

    # Editors only
    url(r'^writer/(?P<writer_id>\d+)/$', writer_blurbs, name='writer_blurbs'),
    url(r'^writer/(?P<writer_id>\d+)/(?P<status>\w+)/$', writer_blurbs, name='writer_blurbs_by_status'),
    url(r'^writer/(?P<writer_id>\d+)/(?P<year>\d+)/$', writer_blurbs, name='writer_blurbs_by_year'),
    url(r'^writer/(?P<writer_id>\d+)/(?P<year>\d+)/(?P<status>\w+)/$', writer_blurbs, name='writer_blurbs_by_year_and_status'),

]