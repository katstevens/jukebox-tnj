from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from blurber.models import Song, ScheduledWeek, Review
from blurber.forms import ReviewForm, UploadSongForm, SortReviewsFormSet


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
            'score_limit': range(0,11),
            'preview_text': preview_text,
            'use_html': use_html
        }
    )


@staff_member_required
def upload_song(request):

    song = False
    if request.method == 'POST':
        form = UploadSongForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            song = form.save(commit=False)
            song.status = 'open'    # Can change in admin later
            song.save()

            if 'submit_and_return_to_songlist' in request.POST:
                return redirect('weekly_schedule')

            # Else reset fresh form for next upload

    form = UploadSongForm()

    return render(
        request, 'upload_song.html', {'form': form, 'song': song}
    )


@staff_member_required
def view_reviews(request, song_id):
    # View all reviews for a song and change ordering

    song = get_object_or_404(Song, id=song_id)
    reviews = Review.objects.filter(song_id=song_id).order_by('sort_order')

    if request.method == 'POST':
        formset = SortReviewsFormSet(data=request.POST)
        if formset.is_valid():
            instances = formset.save()

            if 'submit_and_return_to_songlist' in request.POST:
                return redirect('weekly_schedule')

    return render(
        request,
        'view_reviews.html',
        {'formset': SortReviewsFormSet(queryset=reviews), 'song': song, 'review_count': reviews.count()}
    )


@staff_member_required
def move_review(request, review_id, direction="top"):
    # Bump review to top or bottom
    review = get_object_or_404(Review, id=review_id)
    all_reviews = Review.objects.filter(song=review.song).order_by('sort_order')

    if direction == 'top':
        if review.sort_order > 0:
            review.sort_order = 0
            review.save()
            for r in all_reviews.filter(sort_order__lt=review.sort_order):
                r.sort_order += 1
                r.save()
    if direction == 'bottom':
        if review.sort_order < all_reviews.count():
            review.sort_order = all_reviews.count()
            review.save()
            for r in all_reviews.filter(sort_order__gt=review.sort_order):
                r.sort_order -= 1
                r.save()

    return redirect('view_reviews', review.song.id)


"""
TODO: output HTML for wordpress/tumblr
- wordpress link up/publish
- admin groups (editor, site admin)
- settings per post, turn on/off user ratings (admin)
- deleting blurbs (email alert to admins)
- passwords etc
Edit someone else's blurbs
Look at all blurbs submitted by someone
Change the score
- Upload a song (in progress)
- Edit song info (admin)
- Schedule a day/remove the songs for a day (admin)
Post an entry
"""
