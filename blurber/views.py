from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404

from blurber.models import Song, ScheduledWeek, Review
from blurber.forms import ReviewForm


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
        'song.html',
        {
            'form': form,
            'song': song,
            'score_limit': range(0,11),
            'preview_text': preview_text,
            'use_html': use_html
        }
    )


