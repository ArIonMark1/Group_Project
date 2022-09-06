import pytz
from createapp.models import Room, OfferImages, Convenience, ConvenienceRoom, RoomCategory
from detailsapp.models import OffersRatings, CurrentRentals
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import ListView

from datetime import datetime, timedelta
from pprint import pprint

from lxml import html
from .utils import create_url, get_response, validate_data


# from mainapp.forms import SearchMainForm


def get_yandex_news(dom):
    list_of_news = []
    news_list = dom.xpath("//div[contains(@class, 'mg-card_flexible')]")

    for news in news_list:
        news_info = {}

        name_of_the_news = news.xpath(".//a[@class='mg-card__link']/text()")
        news_link = news.xpath(".//a[@class='mg-card__link']/@href")
        news_date = news.xpath(".//span[@class='mg-card-source__time']/text()")
        news_annotation = news.xpath(".//div[@class='mg-card__annotation']/text()")
        news_source = news.xpath(".//a[@class='mg-card__source-link']/text()")
        news_image_link = news.xpath(".//img[contains(@class, 'neo-image')]/@src")
        if len(news_image_link) == 0:
            news_image_link = news.xpath(".//div[contains(@class, 'mg-card__media-block_type_image')]/@style")
            try:
                news_image_link = news_image_link[0]
                news_image_link = news_image_link[news_image_link.find('(') + 1:news_image_link.find(')')]
                news_info['image'] = news_image_link
            except:
                break
        else:
            news_info['image'] = news_image_link[0]

        news_info['source'] = news_source[0]
        news_info['name'] = validate_data(name_of_the_news[0])
        news_info['link'] = news_link[0]
        news_info['date'] = f'{date.today()}T{news_date[0]}+03:00'
        news_info['text'] = news_annotation[0]

        list_of_news.append(news_info)
    return list_of_news


def get_news_data(site):
    url = create_url(site)
    response = get_response(url)
    dom = html.fromstring(response.text)
    news_data = get_yandex_news(dom)

    return news_data


def get_conveniences():
    return Convenience.objects.all()


def get_room_category():
    return RoomCategory.objects.all()


def get_offers():
    return Room.objects.filter(is_active=True).order_by('payment_per_hour')


def add_images_info(rooms):
    offers_dict = {}
    for room in rooms:
        room_images = OfferImages.objects.filter(room=room)
        room_images = [_ for _ in room_images]
        rooms[room].update({'images': room_images})
        offers_dict[room] = room_images
    return offers_dict


def add_ratings(rooms):
    rooms_dict = {}
    for room in rooms:
        room_rating_info = OffersRatings.objects.filter(
            Q(offer=room))
        room_rating_info = [_ for _ in room_rating_info]

        rooms_dict[room] = {'rating': room_rating_info}
    return rooms_dict


def filter_by_ratings(rooms, rating):
    rooms_dict = {}
    for room in rooms:
        room_rating_info = OffersRatings.objects.filter(
            Q(offer=room),
            Q(summary_rating__gte=rating))
        room_rating_info = [_ for _ in room_rating_info]
        if room_rating_info:
            rooms_dict[room] = {'rating': room_rating_info}
    return rooms_dict


def rental_time_in_range(search_start_date, search_end_date, rental_start_date, rental_end_date):
    """
    Функция, проверяющая, что даты аренды попадают в диапазон, указанный в поисковом запросе
    """
    if search_start_date <= rental_start_date <= search_end_date:
        return True
    elif search_start_date <= rental_end_date <= search_end_date:
        return True
    elif rental_start_date < search_start_date and search_end_date < rental_end_date:
        return True
    else:
        return False


def daterange(start_date, end_date):
    """
    Функция для итерации по диапазону дат
    p.s. try to use dateutil library
    https://overcoder.net/q/36175/%D0%B8%D1%82%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D0%BF%D0%BE-
    %D0%B4%D0%B8%D0%B0%D0%BF%D0%B0%D0%B7%D0%BE%D0%BD%D1%83-%D0%B4%D0%B0%D1%82-%D0%B2-python
    """
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def count_seats_in_rentals_by_days(room_rentals, dates) -> dict:
    """
    Функция расчёта занятых мест в помещении по датам.
    room_rentals: список с арендами, даты которых попадают в поисковый диапазон
    dates: словарь с датами, указанными в поисковом запросе
    return: словарь в котором ключ - дата, значение - кол-во занятых мест
    """
    room_seats_by_days = dict()

    for current_rent in room_rentals:
        for rental_date in daterange(current_rent.start_date.date(), current_rent.end_date.date()):
            seats_count = 0
            if dates['date_from'] <= rental_date <= dates['date_to']:
                seats_count += current_rent.seats
                key = f'{rental_date}'
                if key in room_seats_by_days.keys():
                    room_seats_by_days[key] += seats_count
                else:
                    room_seats_by_days[key] = seats_count

    return room_seats_by_days


def check_that_room_has_free_seats(room, dates):
    """
    Функция проверки свободных мест в помещениях в указанном диапазоне дат.
    Возвращает True если есть свободные места. Иначе False
    """
    qs = CurrentRentals.objects.filter(
        Q(offer=room),
    )
    # temp = [_ for _ in qs]
    room_rentals = [_ for _ in qs if
                    rental_time_in_range(search_start_date=dates['date_from'],
                                         search_end_date=dates['date_to'],
                                         rental_start_date=_.start_date.date(),
                                         rental_end_date=_.end_date.date())]

    counted_seats_by_day = count_seats_in_rentals_by_days(room_rentals, dates)

    max_seats = room.seats_number
    for val in counted_seats_by_day.values():
        if val >= max_seats:
            return False

    return True


def filter_by_dates(rooms, dates):
    if dates:
        filtered_rooms_dict = dict()
        for room in rooms:
            if check_that_room_has_free_seats(room, dates):
                filtered_rooms_dict[room] = rooms[room]
        return filtered_rooms_dict
    else:
        return rooms


def get_actions():
    '''
    функция получения акций для посетителей
    '''
    actions = {
        'name': 'Скидка первым посетителям',
        'text': 'В июле первые 10 заказчиков получат скидку за аренду 25%',
    }
    return actions


def get_conveniences_name():
    conveniences = Convenience.objects.values('name')
    conv_names = []
    for elem in conveniences:
        conv_names.append(elem['name'])
    return conv_names


def get_categories_name():
    categories = RoomCategory.objects.values('name')
    cat_names = []
    for elem in categories:
        cat_names.append(elem['name'])
    return cat_names


def get_convenience_from_request(request):
    request_list = list(request)
    conv_names = get_conveniences_name()

    requested_conveniences = {}

    for elem in request_list:
        if elem in conv_names:
            conv = list(Convenience.objects.filter(name=elem))[0]
            requested_conveniences[elem] = conv.id

    return requested_conveniences


def get_categories_from_request(request):
    request_list = list(request)
    categories_names = get_categories_name()

    requested_categories = []

    for elem in request_list:
        if elem in categories_names:
            # category = RoomCategory.objects.filter(name=elem)
            # requested_categories[elem] = category.id
            requested_categories.append(elem)
    return requested_categories


def get_dates_from_request(request):
    requested_dates = dict()

    try:
        start_date = datetime.strptime(f"{request.get('date_from')}", "%Y-%m-%d").date()
    except ValueError:
        start_date = request.get('date_from')

    try:
        end_date = datetime.strptime(f"{request.get('date_to')}", "%Y-%m-%d").date()
    except ValueError:
        end_date = request.get('date_to')

    if start_date:
        requested_dates['date_from'] = start_date
    if end_date:
        requested_dates['date_to'] = end_date

    return requested_dates


def get_room_conveniences(room_with_convenience):
    room_conveniences = []
    for elem in room_with_convenience:
        room_conveniences.append(elem.convenience_id)

    return room_conveniences


def add_conveniences_in_dict(rooms: dict):
    pass


def main(request):
    title = 'ЛОКАЦИЯ | Каталог помещений'

    offers_list = get_offers()
    offers_dict = add_images_info(offers_list)
    current_actions = get_actions()
    news_list = get_news_data('yandex.ru/news')
    conveniences_list = get_conveniences()

    # paginator = Paginator(offers_list, 5)
    #
    # try:
    #     offers_paginator = paginator.page(page)
    # except PageNotAnInteger:
    #     offers_paginator = paginator.page(1)
    # except EmptyPage:
    #     offers_paginator = paginator.page(paginator.num_pages)
    # print(offers_list)

    context = {
        'title': title,
        'offers_list': offers_list,
        # 'offers_list': offers_paginator,
        'actions': current_actions,
        'offers_dict': offers_dict,
        'news_list': news_list,
        'conveniences_list': conveniences_list,
    }

    return render(request, 'offersapp/index.html', context)


class SearchResultsView(ListView):
    model = Room
    template_name = 'offersapp/search_results.html'
    conveniences = get_conveniences()
    room_categories = get_room_category()
    requested_dates = dict()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SearchResultsView, self).get_context_data()

        context['offers_dict'] = add_images_info(context['object_list'])
        # context['news_list'] = get_news_data('yandex.ru/news')
        context['title'] = 'ЛОКАЦИЯ | Поиск помещений'
        context['date_from'] = self.requested_dates.get('date_from')
        context['date_to'] = self.requested_dates.get('date_to')
        context['city'] = self.request.GET.get('city')
        context['min_price'] = self.request.GET.get('min_price')
        context['max_price'] = self.request.GET.get('max_price')
        context['rating'] = self.request.GET.get('rating')
        context['conveniences_list'] = self.conveniences
        context['room_categories'] = self.room_categories

        return context

    def get_queryset(self):

        city = self.request.GET.get('city')
        requested_category = get_categories_from_request(self.request.GET)
        requested_rating = self.request.GET.get('rating')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')

        requested_rating = int(requested_rating) if requested_rating else 0
        min_price = int(min_price) if min_price else 0
        max_price = int(max_price) if max_price else 10 ** 9

        # отфильтруем помещения по городу и стоимости за час
        rooms_filtered_by_city_and_price = Room.objects.filter(
            Q(is_active=True),
            Q(address__city__icontains=city),
            Q(category__name__in=requested_category) if requested_category else Q(),
            Q(payment_per_hour__gte=min_price),
            Q(payment_per_hour__lte=max_price)
        )

        rooms_filtered_by_city_price = [_ for _ in rooms_filtered_by_city_and_price]

        # проверим наличие в условиях поиска рейтинга
        if requested_rating:
            rooms_filtered_by_city_price_rating = filter_by_ratings(rooms_filtered_by_city_price,
                                                                    requested_rating)
        else:
            rooms_filtered_by_city_price_rating = add_ratings(rooms_filtered_by_city_price)

        requested_conveniences = get_convenience_from_request(self.request.GET)

        # проверим наличие в условиях поиска каких-либо удобств
        if requested_conveniences:
            # rooms_filtered_by_city_price_rating_conv = []
            rooms_filtered_by_city_price_rating_conv = {}

            for room in rooms_filtered_by_city_price_rating:
                room_with_convenience = ConvenienceRoom.objects.filter(room_id=room.id)

                # проверка на наличие в помещениях каких-либо дополнительных удобств
                if room_with_convenience:
                    # print(f'room "{room.name}" is in ConvenienceRoom')

                    # сначала получим список с id всех удобств в помещении
                    room_conveniences = get_room_conveniences(room_with_convenience)
                    # теперь проверяем - есть ли в помещении те удобства, которые запросили при поиске
                    if set(requested_conveniences.values()).issubset(room_conveniences):
                        rooms_filtered_by_city_price_rating_conv[room] = rooms_filtered_by_city_price_rating.get(room)
                        # add_conviences(rooms_filtered_by_city_price_rating_conv[room])
        else:
            rooms_filtered_by_city_price_rating_conv = rooms_filtered_by_city_price_rating

        self.requested_dates = get_dates_from_request(self.request.GET)

        rooms_filtered_by_city_price_rating_conv_date = filter_by_dates(rooms_filtered_by_city_price_rating_conv,
                                                                        self.requested_dates)

        return rooms_filtered_by_city_price_rating_conv_date
