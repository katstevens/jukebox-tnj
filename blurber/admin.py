from django.contrib import admin
from blurber.models import Review, Song, ScheduledWeek


class SongAdmin(admin.ModelAdmin):

    list_display = ['artist', 'title', 'status', 'publish_date']
    list_filter = ['status']
    ordering = ['-publish_date']
    search_fields = ['artist', 'title']


admin.site.register(Review)
admin.site.register(Song, SongAdmin)
admin.site.register(ScheduledWeek)
