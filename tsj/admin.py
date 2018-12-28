from django.contrib import admin
from tsj.models import PublicPost


class PublicPostAdmin(admin.ModelAdmin):

    list_display = ['song', 'published_on', 'visible', 'include_in_search_results']
    ordering = ['-published_on']
    readonly_fields = ['published_on', 'song']
    fields = ['song', 'html_content', 'visible', 'include_in_search_results', 'published_on']
    search_fields = ['song__artist', 'song__title']


admin.site.register(PublicPost, PublicPostAdmin)
