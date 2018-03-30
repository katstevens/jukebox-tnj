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

from django.views.generic.base import TemplateView

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^blurbs/', include('writers.urls')),
    url(r'', include('tsj.urls')),

    url(r'', include('blurber.urls')),
    url(r'', include('django.contrib.auth.urls')),

    url(r'^404testing/$', TemplateView.as_view(template_name='404.html')),
    url(r'^500testing/$', TemplateView.as_view(template_name='500.html'))

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)