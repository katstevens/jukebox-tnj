from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from blurber.models import Review
from writers.models import Writer


CURRENT_YEAR = datetime.now().year


@login_required()
def my_blurbs(request, status=None, year=None):

    reviews = Review.objects.filter(writer=request.user).exclude(status='removed')

    filter_year = year if year else CURRENT_YEAR
    reviews = reviews.filter(create_date__year=filter_year)

    if status == 'saved':
        reviews = reviews.filter(song__status__in=['open', 'closed'])
    elif status == 'published':
        reviews = reviews.filter(song__status='published')

    return render(
        request,
        'my_blurbs.html',
        {
            'reviews': reviews,
            'status': status,
            'year': year,
            'writer': request.user,
            'editor_view': False
        }
    )


@staff_member_required(login_url='login')
def writer_blurbs(request, writer_id, status=None, year=None):
    # An editor can view all the blurbs for a writer
    # with links to edit it in the admin...
    # TODO: restrict editors admin privileges to blurb only
    writer = get_object_or_404(Writer, id=writer_id)
    reviews = Review.objects.filter(writer=writer).exclude(status='removed')

    filter_year = year if year else CURRENT_YEAR
    reviews = reviews.filter(create_date__year=filter_year)

    if status == 'saved':
        reviews = reviews.filter(song__status__in=['open', 'closed'])
    elif status == 'published':
        reviews = reviews.filter(song__status='published')

    return render(
        request,
        'my_blurbs.html',
        {
            'reviews': reviews,
            'status': status,
            'year': year,
            'writer': writer,
            'editor_view': True
        }
    )