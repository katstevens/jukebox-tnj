from datetime import datetime
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.html import escape
from django.utils import timezone

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.exceptions import ServerConnectionError
from wordpress_xmlrpc.methods.posts import NewPost

from blurber.models import Song, ScheduledWeek, Review
from blurber.forms import ReviewForm, UploadSongForm


# Writer views

@login_required
def weekly_schedule(request):

    all_open_songs = Song.objects.filter(status='open')
    user_reviews = Review.objects.filter(song__in=all_open_songs, writer=request.user)

    try:
        this_week = get_object_or_404(ScheduledWeek, current_week=True)
    except:
        # Get the most recent week
        this_week = ScheduledWeek.objects.all().order_by('-week_beginning')[0]

    return render(
        request,
        'schedule.html',
        {
            'this_week': this_week,
            'all_open_songs': all_open_songs,
            'now': datetime.now(),
            'user_songs': [review.song for review in user_reviews]
        }
    )

@login_required
def write_review(request, song_id, use_html=False):

    song = get_object_or_404(Song, id=song_id, status='open')
    try:
        review = Review.objects.get(writer=request.user, song=song)
        preview_text = True
    except Review.DoesNotExist:
        review = Review(writer=request.user, song=song)
        preview_text = False

    if request.method == 'POST':
        form = ReviewForm(data=request.POST, instance=review)
        if form.is_valid():
            # Save the form
            review = form.save(commit=False)
            review.status = 'saved'
            # Copy backup of blurb (in case of admin change)
            review.blurb_backup = review.blurb
            review.save()

            if 'submit_and_return_to_songlist' in request.POST:
                return redirect('weekly_schedule')
            else:
                if use_html:
                    return redirect('write_review_html', song_id=song.id)
                return redirect('write_review', song_id=song.id)

    else:
        form = ReviewForm(instance=review)

    return render(
        request,
        'write_blurb.html',
        {
            'form': form,
            'song': song,
            'preview_text': preview_text,
            'use_html': use_html
        }
    )


# Editor views

@staff_member_required(login_url="login")
def upload_song(request):

    song = False
    if request.method == 'POST':
        form = UploadSongForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            song = form.save(commit=False)
            song.status = 'open'    # Can change in admin later
            # TODO: copy uploaded link to MP3 link field
            song.save()

            if 'submit_and_return_to_songlist' in request.POST:
                return redirect('weekly_schedule')

            # Else reset fresh form for next upload
            form = UploadSongForm()
    else:
        form = UploadSongForm()

    return render(
        request, 'upload_song.html', {'form': form, 'song': song}
    )


@staff_member_required(login_url="login")
def view_reviews(request, song_id):
    # View all reviews for a song and change ordering
    song = get_object_or_404(Song, id=song_id)
    reviews = Review.objects.filter(song_id=song_id).order_by('sort_order')

    return render(
        request,
        'view_reviews.html',
        {
            'reviews': reviews,
            'song': song,
            'review_count': reviews.count()
        }
    )


@staff_member_required(login_url="login")
def move_review(request, review_id, direction="top"):
    # Bump review to top or bottom, or swap with its neighbour
    review = get_object_or_404(Review, id=review_id)
    all_reviews = Review.objects.filter(song=review.song, status='saved').order_by('sort_order')

    all_other_reviews = all_reviews.exclude(id=review.id)

    if direction == 'top':
        new_review_list = [review] + list(all_other_reviews)
    elif direction == 'bottom':
        new_review_list = list(all_other_reviews) + [review]
    else:
        review_index = None
        for index, item in enumerate(all_reviews):
            if item.id == review.id:
                review_index = index
                break

        new_review_list = list(all_reviews)
        if direction == 'up':
            # Swap review with previous (if there)
            if review_index > 0:
                new_review_list[review_index-1], \
                new_review_list[review_index] = \
                    review, \
                    new_review_list[review_index-1]

        if direction == 'down':
            # Swap review with next (if there)
            if review_index + 1 < len(new_review_list):
                new_review_list[review_index+1], \
                new_review_list[review_index] = \
                    review, \
                    new_review_list[review_index+1]

    # Now re-sort everything
    for i in range(0, all_reviews.count()):
        new_review_list[i].sort_order = i+1
        new_review_list[i].save()

    return redirect('view_reviews', review.song.id)


def _song_html_content(request, song_id, template='preview_source.html', show_admin_links=False):
    # Churn out HTML
    song = get_object_or_404(Song, id=song_id)
    reviews = Review.objects.filter(song_id=song_id).order_by('sort_order')
    return render(request, template, {
        'reviews': reviews, 'song': song, 'show_admin_links': show_admin_links}
    )


@staff_member_required(login_url="login")
def preview_post(request, song_id):
    # Display a nice preview with usual header, links etc
    return _song_html_content(request, song_id, template='preview_post.html', show_admin_links=True)


@staff_member_required(login_url="login")
def fetch_html(request, song_id, show_admin_links=False):
    # Display raw HTML ready for C&P
    resp = _song_html_content(request, song_id, show_admin_links=show_admin_links)
    html_data = escape(resp.content)
    return HttpResponse(html_data)


def _create_wp_post(song, content):
    # Create the NewPost object - see docs at
    # http://python-wordpress-xmlrpc.readthedocs.io/en/latest/ref/wordpress.html
    # We're missing some fields but ehhhh who knows if they even exist anymore
    post = WordPressPost()
    post.title = str(song)
    post.content = content
    post.comment_status = 'open'
    post.ping_status = 'closed'
    post.post_status = 'publish'
    post.post_type = 'post'
    post.excerpt = song.tagline
    # TODO: sort out scheduled post date
    post.date = datetime.now(tz=timezone.utc)
    post.date_modified = datetime.now(tz=timezone.utc)

    return NewPost(post)

def _post_to_wp(post):
    # Keep 3rd party calls separate
    client = Client(
        url=settings.XML_RPC_URL,
        username=settings.XML_RPC_USERNAME,
        password=settings.XML_RPC_PW
    )
    return client.call(post)


@staff_member_required(login_url="login")
def publish_song_to_wordpress(request, song_id):
    """
    ### Raw SQL up in the house (what used to happen)

    INSERT INTO wp_posts
        (id, post_author, post_date, post_date_gmt, post_content, post_title,
        post_category, post_excerpt, post_status, comment_status, ping_status,
        post_password, post_name, to_ping, pinged, post_modified, post_modified_gmt,
        post_content_filtered, post_parent, guid, menu_order, post_type, post_mime_type, comment_count)
    VALUES
        (Default, $post_author, '$postdate', '$postdate', '$actualpost', '$posttitle',
        Default, '$tagline', '$poststatus', 'open', 'closed',
        Default, '$postname', '', '', '$currenttime', '$currenttime',
        '', 0, Default, 0, 'post', '', 0 )

    """
    # Get the content
    song = get_object_or_404(Song, id=song_id)
    resp = _song_html_content(request, song_id, show_admin_links=False)
    html_data = escape(resp.content)

    # Build the post
    post = _create_wp_post(song, html_data)

    # Send it on its merry way
    post_id = _post_to_wp(post)

    # Update blurber
    song.wordpress_post_id = post_id
    song.save()

    return HttpResponse("Song posted successfully - Wordpress ID %s" % post_id)
