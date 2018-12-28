from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from blurber.models import Song
from writers.models import Writer
from tsj.models import PublicPost, Comment
from tsj.forms import CommentForm

from jukebox.settings import POSTS_PER_PAGE

# Public-facing pages

def get_writers():
    return Writer.objects.filter(is_active=True, public=True).order_by('last_name', 'first_name')


def home(request):
    # Legacy redirect: ?p=123 goes to single_post with that Song ID
    if request.GET.get('p'):
        try:
            song_id = int(request.GET['p'])
            return redirect('single_post', song_id=song_id)
        except ValueError:
            # Ignore silently
            pass

    if request.GET.get('s'):
        results = PublicPost.objects.filter(
            html_content__icontains=request.GET['s'],
            include_in_search_results=True,
            visible=True
        )
        return render(
            request,
            template_name="search_results.html",
            context={
                'results': results,
                'page_no': 1,  # TODO: pagination
                'writers': get_writers()
            }
        )

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
    recent_songs = PublicPost.objects.filter(visible=True).order_by('-published_on')[start:end]

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
    song = get_object_or_404(Song, id=song_id)
    comments = Comment.objects.filter(visible=True, song=song).order_by('published_on')
    pp = get_object_or_404(PublicPost, song=song, visible=True)
    # Get prev and next public posts (not Songs)
    try:
        next_song = pp.get_next_by_published_on(visible=True)
    except ObjectDoesNotExist:
        next_song = None
    try:
        prev_song = pp.get_previous_by_published_on(visible=True)
    except ObjectDoesNotExist:
        prev_song = None

    return render(
        request,
        template_name="single_post.html",
        context={
            'pp': pp,
            'writers': get_writers(),
            'form': CommentForm,
            'comments': comments,
            'comment_count': comments.count(),
            'prev_song': prev_song,
            'next_song': next_song
        }
    )


def post_comment(request, song_id):
    if request.method == 'POST':
        song = get_object_or_404(Song, id=song_id)
        form = CommentForm(data=request.POST)
        if form.is_valid():
            # Save the form
            comment = form.save(commit=False)
            comment.song = song
            comment.save()

    return redirect('single_post', song_id)


def about(request):
    return render(request, template_name='about.html')
