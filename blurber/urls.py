from django.conf.urls import url

from blurber.views import (
    weekly_schedule, write_review, upload_song, view_reviews,
    close_song, publish_song,
    preview_post, fetch_html, move_review
)

urlpatterns = [
    url(r'^schedule/', weekly_schedule, name='weekly_schedule'),
    url(r'^song/(?P<song_id>\d+)$', write_review, name='write_review'),
    url(r'^song/(?P<song_id>\d+)/html/$', write_review, {'use_html': True}, name='write_review_html'),

    # Staff only views
    url(r'^song/upload', upload_song, name='upload_song'),
    url(r'^song/(?P<song_id>\d+)/reviews/$', view_reviews, name='view_reviews'),
    url(r'^song/(?P<song_id>\d+)/preview/$', preview_post, name='preview_post'),
    url(r'^song/(?P<song_id>\d+)/source/$', fetch_html, name='fetch_html'),
    url(r'^song/(?P<song_id>\d+)/close/$', close_song, name='close_song'),
    url(r'^song/(?P<song_id>\d+)/publish/$', publish_song, name='publish_song'),
    url(r'^review/(?P<review_id>\d+)/moveup/$', move_review, {'direction': 'up'}, name='move_review_up'),
    url(r'^review/(?P<review_id>\d+)/movedown/$', move_review, {'direction': 'down'}, name='move_review_down'),
    url(r'^review/(?P<review_id>\d+)/movetop/$', move_review, {'direction': 'top'}, name='move_review_top'),
    url(r'^review/(?P<review_id>\d+)/movebottom/$', move_review, {'direction': 'bottom'}, name='move_review_bottom'),
]