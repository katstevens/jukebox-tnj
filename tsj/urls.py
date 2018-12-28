from django.conf.urls import url

from tsj.views import (
    home, single_post, about
)

urlpatterns = [
    url(r'^$', home, name='home_page'),
    url(r'^s/(?P<song_id>\d+)$', single_post, name='single_post'),
    url(r'^about$', about, name='about'),

]