from django.conf.urls import url

from writers.views import my_blurbs

urlpatterns = [
    # The below are included under the /myblurbs url space
    url(r'^$', my_blurbs, name='my_blurbs'),
    url(r'^(?P<status>\w+)/$', my_blurbs, name='my_blurbs_by_status'),
    url(r'^(?P<year>\d+)/$', my_blurbs, name='my_blurbs_by_year'),
    url(r'^(?P<year>\d+)/(?P<status>\w+)/$', my_blurbs, name='my_blurbs_by_year_and_status'),
]