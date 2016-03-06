from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from blurber.models import Review
from writers.models import Writer


CURRENT_YEAR = datetime.now().year


def get_reviews_by_status_and_year(writer, status, year):

    reviews = Review.objects.filter(writer=writer).\
                exclude(status='removed').\
                filter(create_date__year=year)

    if status == 'saved':
        reviews = reviews.filter(song__status__in=['open', 'closed'])
    elif status == 'published':
        reviews = reviews.filter(song__status='published')

    return reviews


@login_required()
def my_blurbs(request, status=None, year=None):

    filter_year = year if year else CURRENT_YEAR
    reviews = get_reviews_by_status_and_year(request.user, status, filter_year)

    return render(
        request,
        'my_blurbs.html',
        {
            'reviews': reviews,
            'status': status,
            'year': filter_year,
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

    filter_year = year if year else CURRENT_YEAR
    reviews = get_reviews_by_status_and_year(writer, status, filter_year)

    return render(
        request,
        'my_blurbs.html',
        {
            'reviews': reviews,
            'status': status,
            'year': filter_year,
            'writer': writer,
            'editor_view': True
        }
    )
