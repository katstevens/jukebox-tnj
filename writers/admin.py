from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from writers.models import Writer


class WriterAdmin(UserAdmin):

    # TODO: include extra fields e.g. bio_link
    list_display = ['first_name', 'last_name', 'is_staff']
    list_filter = ['is_staff']
    ordering = ['last_name', 'first_name']
    search_fields = ['last_name', 'first_name']

admin.site.register(Writer, WriterAdmin)