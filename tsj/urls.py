from django.conf.urls import url

from tsj.views import (
    home, single_post, search, about
)

urlpatterns = [
    url(r'^$', home, name='home_page'),
    url(r'^s/(?P<song_id>\d+)$', single_post, name='single_post'),
    url(r'^search$', search, name='search'),
    url(r'^about$', about, name='about'),

]