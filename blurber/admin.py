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


class SongAdmin(admin.ModelAdmin):

    list_display = ['artist', 'title', 'status', 'publish_date']
    list_filter = ['status']
    ordering = ['-publish_date']
    search_fields = ['artist', 'title']


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
