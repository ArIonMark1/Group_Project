import os

import pytz
from django.conf import settings
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse
from createapp.models import Room, Address, RoomCategory, OfferImages, Convenience, ConvenienceRoom, ConvenienceType
from detailsapp.models import CurrentRentals, Favorites, RatingNames, Evaluations, CompletedRentals, Rating, \
    OffersRatings


def get_active_offer(pk):
    return get_object_or_404(Room, pk=pk, is_active=True)


def get_offer_reviews(offer):
    rating_dict = {}
    qs = Evaluations.objects.filter(offer=offer)
    try:
        for rating_obj in RatingNames.objects.all():
            rating_dict[rating_obj.name] = int(qs.filter(rating_name=rating_obj).aggregate(rating=Avg("evaluation"))[
                                                   'rating'])
    except:
        pass
    reviews = Rating.objects.filter(offer=offer)
    sum_rating = None
    try:
        obj = OffersRatings.objects.get(offer=offer)
        sum_rating = obj.summary_rating
    except:
        pass
    return rating_dict, list(reviews), sum_rating


def datetime_in_range(start_date, end_date, current_start_date, current_end_date):
    if end_date >= current_start_date >= start_date and end_date >= current_end_date >= start_date:
        return True
    elif end_date >= current_start_date >= start_date and end_date <= current_end_date >= start_date:
        return True
    elif end_date >= current_start_date <= start_date <= current_end_date <= end_date:
        return True
    else:
        return False


def get_current_rentals(qs, start_date, end_date):
    return [_ for _ in qs if datetime_in_range(start_date=start_date,
                                               end_date=end_date,
                                               current_start_date=_.start_date,
                                               current_end_date=_.end_date)]


def check_start_time(current_time, start_time):
    if start_time in current_time.strftime("%d/%m/%Y %H:%M:%S"):
        return True
    else:
        return False


def get_available_seats(request, pk, start_date, end_date, seats):
    start_date_str = start_date
    end_date_str = end_date
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        offer = get_active_offer(pk=pk)
        start_date = datetime.strptime(start_date + ' ' + str(offer.start_working_hours), "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=pytz.utc)
        end_date = datetime.strptime(end_date + ' ' + str(offer.end_working_hours), "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=pytz.utc)
        seats_result = []
        delta_hours = int(24 - int(offer.end_working_hours.hour - offer.start_working_hours.hour))
        try:
            qs = list(CurrentRentals.objects.filter(offer=offer).order_by('start_date', 'end_date'))
            if qs[-1].end_date < start_date or qs[0].start_date > end_date:
                raise Exception
            rentals = get_current_rentals(qs=qs, start_date=start_date, end_date=end_date)
            rentals_dates = [_ for _ in sorted(sum([[_.start_date, _.end_date] for _ in rentals], [])) if
                             start_date <= _ <= end_date]
            if rentals_dates[-1] < end_date:
                rentals_dates.append(end_date)
            current_dates = []
            for i, rental_date in enumerate(rentals_dates):
                if rental_date == rentals_dates[i + 1 if i + 1 < len(rentals_dates) else 0] or \
                        rental_date == rentals_dates[i - 1]:
                    try:
                        if current_dates[-1][-1] == rental_date:
                            current_dates[-1].append(rental_date)
                        else:
                            current_dates.append([rental_date])
                    except:
                        current_dates.append([rental_date])
                else:
                    current_dates.append(rental_date)
            prev_date = start_date
            for rental_date in current_dates:
                if type(rental_date) == list:
                    if check_start_time(current_time=rental_date[0], start_time=str(offer.start_working_hours)):
                        if check_start_time(current_time=prev_date, start_time=str(offer.start_working_hours)):
                            if rental_date[0] == prev_date:
                                prev_date = rental_date[0]
                                continue
                            current_end_date = rental_date[0] + timedelta(hours=-delta_hours)
                            current_start_date = prev_date
                            available_seats = offer.seats_number - sum([_.seats for _ in rentals if
                                                                        datetime_in_range(start_date=current_start_date,
                                                                                          end_date=current_end_date,
                                                                                          current_start_date=_.start_date,
                                                                                          current_end_date=_.end_date)])
                            if available_seats >= seats:
                                seats_result.append({
                                    f'{seats}': {
                                        'start_date': current_start_date,
                                        'end_date': current_end_date}
                                })
                            prev_date = rental_date[0]
                        else:
                            current_start_date = prev_date + timedelta(hours=delta_hours)
                            if current_start_date == rental_date[0]:
                                continue
                            current_end_date = rental_date[0] + timedelta(hours=-delta_hours)
                            available_seats = offer.seats_number - sum([_.seats for _ in rentals if
                                                                        datetime_in_range(start_date=current_start_date,
                                                                                          end_date=current_end_date,
                                                                                          current_start_date=_.start_date,
                                                                                          current_end_date=_.end_date)])
                            if available_seats >= seats:
                                seats_result.append({
                                    f'{seats}': {
                                        'start_date': current_start_date,
                                        'end_date': current_end_date}
                                })
                            prev_date = rental_date[0]
                    else:
                        if check_start_time(current_time=prev_date, start_time=str(offer.start_working_hours)):
                            current_start_date = prev_date
                            current_end_date = rental_date[0]
                            available_seats = offer.seats_number - sum([_.seats for _ in rentals if
                                                                        datetime_in_range(start_date=current_start_date,
                                                                                          end_date=current_end_date,
                                                                                          current_start_date=_.start_date,
                                                                                          current_end_date=_.end_date)])
                            if available_seats >= seats:
                                seats_result.append({
                                    f'{seats}': {
                                        'start_date': current_start_date,
                                        'end_date': current_end_date}
                                })
                            prev_date = rental_date[0]
                        else:
                            current_start_date = prev_date + timedelta(hours=delta_hours)
                            current_end_date = rental_date[0]
                            available_seats = offer.seats_number - sum([_.seats for _ in rentals if
                                                                        datetime_in_range(start_date=current_start_date,
                                                                                          end_date=current_end_date,
                                                                                          current_start_date=_.start_date,
                                                                                          current_end_date=_.end_date)])
                            if available_seats >= seats:
                                seats_result.append({
                                    f'{seats}': {
                                        'start_date': current_start_date,
                                        'end_date': current_end_date}
                                })
                            prev_date = rental_date[0]
                else:
                    if check_start_time(current_time=rental_date, start_time=str(offer.start_working_hours)):
                        if check_start_time(current_time=prev_date, start_time=str(offer.start_working_hours)):
                            if rental_date == prev_date:
                                prev_date = rental_date
                                continue
                            current_end_date = rental_date + timedelta(hours=-delta_hours)
                            current_start_date = prev_date
                            available_seats = offer.seats_number - sum([_.seats for _ in rentals if
                                                                        datetime_in_range(start_date=current_start_date,
                                                                                          end_date=current_end_date,
                                                                                          current_start_date=_.start_date,
                                                                                          current_end_date=_.end_date)])
                            if available_seats >= seats:
                                seats_result.append({
                                    f'{seats}': {
                                        'start_date': current_start_date,
                                        'end_date': current_end_date}
                                })
                            prev_date = rental_date
                        else:
                            current_start_date = prev_date + timedelta(hours=delta_hours)
                            if current_start_date == rental_date:
                                continue
                            current_end_date = rental_date + timedelta(hours=-delta_hours)
                            available_seats = offer.seats_number - sum([_.seats for _ in rentals if
                                                                        datetime_in_range(start_date=current_start_date,
                                                                                          end_date=current_end_date,
                                                                                          current_start_date=_.start_date,
                                                                                          current_end_date=_.end_date)])
                            if available_seats >= seats:
                                seats_result.append({
                                    f'{seats}': {
                                        'start_date': current_start_date,
                                        'end_date': current_end_date}
                                })
                            prev_date = rental_date
                    else:
                        if check_start_time(current_time=prev_date, start_time=str(offer.start_working_hours)):
                            current_start_date = prev_date
                            current_end_date = rental_date
                            available_seats = offer.seats_number - sum([_.seats for _ in rentals if
                                                                        datetime_in_range(start_date=current_start_date,
                                                                                          end_date=current_end_date,
                                                                                          current_start_date=_.start_date,
                                                                                          current_end_date=_.end_date)])
                            if available_seats >= seats:
                                seats_result.append({
                                    f'{seats}': {
                                        'start_date': current_start_date,
                                        'end_date': current_end_date}
                                })
                            prev_date = rental_date
                        else:
                            current_start_date = prev_date + timedelta(hours=delta_hours)
                            current_end_date = rental_date
                            available_seats = offer.seats_number - sum([_.seats for _ in rentals if
                                                                        datetime_in_range(start_date=current_start_date,
                                                                                          end_date=current_end_date,
                                                                                          current_start_date=_.start_date,
                                                                                          current_end_date=_.end_date)])
                            if available_seats >= seats:
                                seats_result.append({
                                    f'{seats}': {
                                        'start_date': current_start_date,
                                        'end_date': current_end_date}
                                })
                            prev_date = rental_date
            if len(seats_result) == 0:
                return get_available_seats(request=request, pk=pk, start_date=start_date_str, end_date=end_date_str,
                                           seats=seats - 1)
            seats_result = [_ for _ in seats_result if int(list(_.keys())[0]) > 0]
            if len(seats_result) > 1 and prev_date + timedelta(hours=24 - delta_hours) < end_date:
                current_start_date = prev_date + timedelta(hours=delta_hours)
                current_end_date = end_date
                available_seats = offer.seats_number - sum([_.seats for _ in rentals if
                                                            datetime_in_range(start_date=current_start_date,
                                                                              end_date=current_end_date,
                                                                              current_start_date=_.start_date,
                                                                              current_end_date=_.end_date)])
                if available_seats >= seats:
                    seats_result.append({
                        f'{seats}': {
                            'start_date': current_start_date,
                            'end_date': current_end_date}
                    })
            new_result = []
            prev_seats = 0
            prev_end_date = seats_result[0][list(seats_result[0].keys())[0]]["end_date"]
            for seats_dict in seats_result:
                for k, v in seats_dict.items():
                    if prev_seats == k and (v["start_date"] + timedelta(hours=-delta_hours)) == prev_end_date:
                        new_result[-1][prev_seats]['end_date'] = v["end_date"]
                    else:
                        new_result.append({f'{k}': {'start_date': v["start_date"],
                                                    'end_date': v["end_date"]}
                                           })
                    prev_seats = k
                    prev_end_date = v["end_date"]
            if len(new_result) == 1 and start_date >= new_result[0][list(new_result[0].keys())[0]][
                "start_date"] and end_date <= new_result[0][list(new_result[0].keys())[0]]["end_date"]:
                context = {
                    'available_seats': [_ for _ in range(1, int(list(new_result[0].keys())[0]) + 1)]
                }
                result = render_to_string('detailsapp/includes/inc_seats.html', context)
                return JsonResponse({'result': result})
        except:
            context = {
                'available_seats': [_ for _ in range(1, offer.seats_number + 1)]
            }
            result = render_to_string('detailsapp/includes/inc_seats.html', context)
            return JsonResponse({'result': result})
        seats = {}
        for seats_dict in new_result:
            for k, v in seats_dict.items():
                seats[
                    f'с {v["start_date"].strftime("%d/%m/%Y %H:%M")} до {v["end_date"].strftime("%d/%m/%Y %H:%M")}'] = k
        context = {
            'seats': seats
        }
        result = render_to_string('detailsapp/includes/inc_seats.html', context)
        return JsonResponse({'result': result})


def get_offer_context(offer):
    try:
        offer_address = get_object_or_404(Address, pk=offer.address.pk)
        category = get_object_or_404(RoomCategory, pk=offer.category.pk)
        offer_images = OfferImages.objects.filter(room=offer)
        conv_types = []
        conveniences = list(Convenience.objects.all())
        room_conveniences_id = [_.convenience_id for _ in ConvenienceRoom.objects.filter(room_id=offer.pk)]
        for conv_type in ConvenienceType.objects.all():
            type_dict = {}
            conv_types.append(type_dict)
            type_dict['name'] = conv_type.name
            type_dict['conveniences'] = list(
                map(
                    lambda it:
                    {'name': it.name,
                     'id': it.pk,
                     'html': read_template(it.file_name)},
                    filter(lambda it: it.convenience_type == conv_type, conveniences)
                )
            )
        context = {
            'title': offer.name,
            'offer': offer,
            'offer_address': offer_address,
            'category': category,
            'seats_number': [_ for _ in range(1, offer.seats_number + 1)],
            'offer_images': offer_images,
            'owner': offer.room_owner,
            'convenience_types': conv_types,
            'conveniences': conveniences,
            'room_conveniences_id': room_conveniences_id,
        }
        return context
    except:
        return None


def read_template(file_name):
    with open(os.path.join(settings.BASE_DIR,
                           'createapp', 'templates', 'createapp', 'includes', 'amenities', file_name), 'r') as file:
        return file.read().rstrip()


def show_details(request, pk):
    try:
        offer = get_active_offer(pk=pk)
        context = get_offer_context(offer=offer)
        rating_dict, reviews, sum_rating = get_offer_reviews(offer=offer)
        context['rating_dict'] = rating_dict
        context['reviews'] = reviews
        context['sum_rating'] = sum_rating
        if not request.user.is_anonymous:
            context['in_fav'] = Favorites.objects.filter(user=request.user, offer__pk=pk).exists()
        else:
            context['in_fav'] = False
        refs = request.META.get('HTTP_REFERER', '')
        if 'user/bookings' in refs or \
                'user/locations' in refs or \
                'admin' in refs:
            context['show'] = False
        else:
            context['show'] = True
        return render(request, 'detailsapp/details.html', context=context)
    except:
        return render(request, 'detailsapp/error.html')


@login_required()
def create_rental(request, pk):
    offer = get_object_or_404(Room, pk=pk)
    start_date = datetime.strptime(f"{request.POST['start_date'] + ' ' + str(offer.start_working_hours)}",
                                   "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime(f"{request.POST['end_date'] + ' ' + str(offer.end_working_hours)}",
                                 "%Y-%m-%d %H:%M:%S")
    working_hours = int((end_date - start_date).days * int((end_date - start_date).seconds / 3600) +
                        int((end_date - start_date).seconds / 3600))
    CurrentRentals(
        user=request.user,
        offer=offer,
        seats=int(request.POST['seats']),
        start_date=start_date,
        end_date=end_date,
        amount=int(offer.payment_per_hour * working_hours * int(request.POST['seats'])),
    ).save()
    return HttpResponseRedirect(reverse('user:bookings'))


def send_review(request, pk):
    if request.method == 'POST':
        rental = get_object_or_404(CurrentRentals, pk=pk)
        qs = RatingNames.objects.all()
        rating_sum = int()
        for name_obj in qs:
            evaluation = int(request.POST[f'rating-value{name_obj.id}'])
            rating_sum += evaluation
            Evaluations(
                user=request.user,
                offer=rental.offer,
                rating_name=name_obj,
                evaluation=evaluation,
            ).save()
        summary_evaluation = float(f'{(rating_sum / len(qs)):.1f}')
        Rating(
            user=request.user,
            offer=rental.offer,
            review_text=request.POST['review-text'],
            summary_evaluation=summary_evaluation,
        ).save()
        try:
            offer_rating = OffersRatings.objects.get(offer=rental.offer)
            offer_rating.summary_rating = float(
                f'{((offer_rating.summary_rating * offer_rating.reviews_number) + summary_evaluation) / (offer_rating.reviews_number + 1):.1f}'
            )
            offer_rating.reviews_number += 1
            offer_rating.save()
        except:
            OffersRatings(
                offer=rental.offer,
                summary_rating=summary_evaluation,
                reviews_number=1,
            ).save()
        CompletedRentals(
            user=request.user,
            offer=rental.offer,
            seats=rental.seats,
            start_date=rental.start_date,
            end_date=rental.end_date,
            amount=rental.amount,
        ).save()
        rental.delete()
        return HttpResponseRedirect(reverse('user:bookings'))
    else:
        rating_names = RatingNames.objects.all()
        context = {
            'title': 'title',
            'rating_names': rating_names,
        }
        return render(request, 'detailsapp/offer_feedback.html', context=context)


@login_required()
def add_favorite(request, pk):
    obj, created = Favorites.objects.get_or_create(user=request.user, offer=get_object_or_404(Room, pk=pk))
    if created:
        obj.save()
    return HttpResponseRedirect(reverse('user:favorites'))


@login_required()
def del_favorite(request, pk):
    favorites = Favorites.objects.filter(user=request.user, offer__pk=pk)
    for fav in favorites:
        fav.delete()
    return HttpResponseRedirect(reverse('user:favorites'))
