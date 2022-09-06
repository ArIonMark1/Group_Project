from django.shortcuts import render, redirect

from createapp.models import Room, OfferImages
from detailsapp.models import OffersRatings
from mainapp.forms import SearchMainForm


def main(request):
    title = 'ЛОКАЦИЯ | Сервис для поиска коворкинга в России'

    has_query = len(request.GET) > 0

    if has_query:
        form = SearchMainForm(data=request.GET)
    else:
        form = SearchMainForm()
    offer_ratings = list(OffersRatings.objects.order_by('-summary_rating')[:3])
    rooms = list(map(lambda x: x.offer, offer_ratings))
    offer_images = OfferImages.objects.filter(room__in=rooms)

    room_data = {}

    for rating in offer_ratings:
        room_data[rating.offer] = {
            'rating': rating.summary_rating
        }

    for image in offer_images:
        room_data[image.room]['image'] = image.image

    context = {
        'title': title,
        'form': form,
        'room_data': room_data
    }
    if has_query and form.is_valid():
        return redirect('offers/search/?' + request.GET.urlencode())
    return render(request, 'mainapp/index.html', context)
