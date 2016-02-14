from django.contrib import admin
from blurber.models import Review, Song, ScheduledWeek

# Register your models here.
admin.site.register(Review)
admin.site.register(Song)
admin.site.register(ScheduledWeek)