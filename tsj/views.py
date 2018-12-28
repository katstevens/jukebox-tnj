from django.shortcuts import render, redirect, get_object_or_404
from blurber.models import Song
from writers.models import Writer
from tsj.models import PublicPost

from jukebox.settings import POSTS_PER_PAGE

# Public-facing pages

def get_writers():
    return Writer.objects.filter(is_active=True, public=True).order_by('last_name', 'first_name')


def home(request):
    # Legacy redirect: ?p=123 goes to single_post with that ID
    if request.GET.get('p'):
        try:
            song_id = int(request.GET['p'])
            return redirect('single_post', song_id=song_id)
        except ValueError:
            # Ignore silently
            pass

    # Pagination
    page = 1
    if request.GET.get('paged'):
        try:
            page = int(request.GET['paged'])
        except ValueError:
            pass

    # Get last X songs (X determined by setting) offset by <page>
    start, end = 0, POSTS_PER_PAGE
    if page > 1:
        end = page*5
        start = end - POSTS_PER_PAGE
    recent_songs = Song.objects.filter(status='published').order_by('-publish_date')[start:end]

    return render(
        request,
        template_name="home_page.html",
        context={
            'recent_songs': recent_songs,
            'page_no': page,
            'writers': get_writers()
        }
    )


def single_post(request, song_id):
    song = get_object_or_404(Song, id=song_id, status='published')
    return render(
        request,
        template_name="single_post.html",
        context={
            'song': song,
            'writers': get_writers()
        }
    )


def search(request):
    if request.method == 'GET':
        return redirect('home_page')
    else:
        # TODO: Proper search functionality
        if request.GET.get('q'):
            results = PublicPost.objects.filter(
                html_content__unaccent__icontains=request.GET['q'],
                include_in_search_results=True,
                visible=True
            )
        else:
            results = []

    return render(
        request,
        template_name="search_results.html",
        context={
            'results': results,
            'writers': get_writers()
        }
    )


def about(request):
    return render(request, template_name='about.html')
