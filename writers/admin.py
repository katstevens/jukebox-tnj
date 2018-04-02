from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from writers.models import Writer


class WriterAdmin(UserAdmin):

    list_display = ['first_name', 'last_name', 'username', 'is_staff', 'date_joined']
    list_filter = ['is_staff']
    ordering = ['last_name', 'first_name']
    search_fields = ['last_name', 'first_name']

    fieldsets = UserAdmin.fieldsets + (
        ("Blogroll info", {
            'fields': ('bio_link', 'bio_link_name',)
        }),
    )


admin.site.register(Writer, WriterAdmin)
