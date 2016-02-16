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
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin

from blurber.views import weekly_schedule, write_review
from writers.views import my_blurbs

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^schedule/', weekly_schedule, name='weekly_schedule'),
    url(r'^song/(?P<song_id>\d+)$', write_review, name='write_review'),
    url(r'^song/(?P<song_id>\d+)/html/$', write_review, {'use_html': True}, name='write_review_html'),

    url(r'^myblurbs/$', my_blurbs, name='my_blurbs'),
    url(r'^myblurbs/(?P<status>\w+)/$', my_blurbs, name='my_blurbs_by_status'),
    url(r'^myblurbs/(?P<year>\d+)/$', my_blurbs, name='my_blurbs_by_year'),
    url(r'^myblurbs/(?P<year>\d+)/(?P<status>\w+)/$', my_blurbs, name='my_blurbs_by_year_and_status'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)