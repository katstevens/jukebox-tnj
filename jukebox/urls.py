"""jukebox URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from blurber.views import (
    weekly_schedule, write_review, upload_song, view_reviews, move_review, preview_post, fetch_html
)

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^schedule/', weekly_schedule, name='weekly_schedule'),
    url(r'^song/(?P<song_id>\d+)$', write_review, name='write_review'),
    url(r'^song/(?P<song_id>\d+)/html/$', write_review, {'use_html': True}, name='write_review_html'),

    # Staff only views
    url(r'^song/upload', upload_song, name='upload_song'),
    url(r'^song/(?P<song_id>\d+)/reviews/$', view_reviews, name='view_reviews'),
    url(r'^song/(?P<song_id>\d+)/preview/$', preview_post, name='preview_post'),
    url(r'^song/(?P<song_id>\d+)/source/$', fetch_html, name='fetch_html'),
    url(r'^review/(?P<review_id>\d+)/moveup/$', move_review, {'direction': 'up'}, name='move_review_up'),
    url(r'^review/(?P<review_id>\d+)/movedown/$', move_review, {'direction': 'down'}, name='move_review_down'),
    url(r'^review/(?P<review_id>\d+)/movetop/$', move_review, {'direction': 'top'}, name='move_review_top'),
    url(r'^review/(?P<review_id>\d+)/movebottom/$', move_review, {'direction': 'bottom'}, name='move_review_bottom'),

    url(r'^myblurbs/', include('writers.urls')),
    url(r'', include('django.contrib.auth.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)