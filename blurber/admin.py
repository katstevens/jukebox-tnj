from django.conf import settings
from django.contrib import admin
from django.core.mail import send_mail
from blurber.models import Review, Song, ScheduledWeek


def send_email_if_blurb_removed(obj, user):
    subject = "Blurb removed: %s" % obj
    message = "The following blurb has been removed from the TSJ 2.0 admin " \
              "by user %s:\n\n%s\n\n" % (user, obj)
    result = send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_FROM_ADDRESS,
        recipient_list=settings.EMAIL_ADMINS
    )
    return result


class ScheduledWeekAdmin(admin.ModelAdmin):

    list_display = ['week_beginning', 'week_summary']
    ordering = ['-week_beginning']
    readonly_fields = ['monday_songs', 'tuesday_songs', 'wednesday_songs',
                       'thursday_songs', 'friday_songs', 'saturday_songs', ]
    fields = (
        'week_beginning', 'week_info',
        ('monday', 'monday_songs'),
        ('tuesday', 'tuesday_songs'),
        ('wednesday', 'wednesday_songs'),
        ('thursday', 'thursday_songs'),
        ('friday', 'friday_songs'),
        ('saturday', 'saturday_songs'),
        'current_week'
    )

class SongAdmin(admin.ModelAdmin):

    def search_reviews_link(self, obj):
        return obj.admin_review_search_link
    search_reviews_link.short_description = ''
    search_reviews_link.allow_tags = True

    list_display = ['artist', 'title', 'status', 'publish_date']
    list_filter = ['status']
    ordering = ['-publish_date']
    search_fields = ['artist', 'title']
    readonly_fields = ['search_reviews_link']

    fieldsets = (
        (None, {
            'fields': ('artist', 'title', 'status', 'search_reviews_link')
        }),
        ("Media links", {
            'fields': ('youtube_link', 'mp3_file', 'mp3_link')
        }),
        ('Publishing options', {
            'fields': ('tagline', 'image_url',  'web_link', 'publish_date'),
        }),
    )


class ReviewAdmin(admin.ModelAdmin):

    list_display = ['song', 'writer', 'score']
    list_filter = ['status']
    ordering = ['song__artist', 'song__title', 'sort_order']
    search_fields = ['song__artist', 'song__title', 'writer__username', 'writer__first_name', 'writer__last_name']
    # Admin shouldn't be able to change another writer's score or backup blurb
    readonly_fields = ['score', 'blurb_backup']

    def save_model(self, request, obj, form, change):
        # Email admin if blurb removed
        if change and 'status' in form.changed_data:
            if form.cleaned_data['status'] == "removed":
                sent = send_email_if_blurb_removed(obj, request.user)

        obj.save()

admin.site.register(Review, ReviewAdmin)
admin.site.register(Song, SongAdmin)
admin.site.register(ScheduledWeek, ScheduledWeekAdmin)
