from django.contrib import admin
from blurber.models import Review, Song, ScheduledWeek


class SongAdmin(admin.ModelAdmin):

    list_display = ['artist', 'title', 'status', 'publish_date']
    list_filter = ['status']
    ordering = ['-publish_date']
    search_fields = ['artist', 'title']


class ReviewAdmin(admin.ModelAdmin):

    list_display = ['song', 'writer', 'sort_order']
    list_filter = ['status']
    ordering = ['song__artist', 'song__title', 'sort_order']
    search_fields = ['song__artist', 'song__title', 'writer__username', 'writer__first_name', 'writer__last_name']


admin.site.register(Review, ReviewAdmin)
admin.site.register(Song, SongAdmin)
admin.site.register(ScheduledWeek)
