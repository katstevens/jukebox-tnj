from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404

from blurber.models import Review


CURRENT_YEAR = datetime.now().year


def my_blurbs(request, status=None, year=None):

    reviews = Review.objects.filter(writer=request.user).exclude(status='removed')

    filter_year = year if year else CURRENT_YEAR
    reviews = reviews.filter(create_date__year=filter_year)

    if status == 'open':
        reviews = reviews.filter(song__status__in=['open', 'closed'])
    elif status == 'published':
        reviews = reviews.filter(song__status='published')

    return render(
        request,
        'my_blurbs.html',
        {
            'reviews': reviews,
            'status': status,
            'year': year
        }
    )
