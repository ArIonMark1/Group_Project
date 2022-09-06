from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView
from django.contrib import auth, messages
from django.shortcuts import redirect
from adminapp.models import Claim
from createapp.models import Room, OfferImages
from detailsapp.models import CurrentRentals, CompletedRentals, Favorites
from userapp.models import UserModel
from userapp.forms import UserForm, LandlordApplicationForm
from django.urls import reverse_lazy

from userapp.forms import PasswordChangeCustomForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from createapp.views import read_template
from createapp.models import OfferImages, ConvenienceType, Convenience, ConvenienceRoom, Address
from createapp.forms import ImageForm
from createapp.geo_checker import check_address
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.db import transaction
from .forms import CreateAdForm


@login_required
def users(request, pk):
    title = 'Админка - Пользователь'

    this_user = get_object_or_404(UserModel, pk=pk)

    context = {
        'title': title,
        'this_user': this_user
    }
    return render(request, 'userapp/users.html', context)


@login_required
def user(request):
    title = 'ЛОКАЦИЯ | Личный кабинет'

    context = {
        'title': title,
    }
    return render(request, 'userapp/user.html', context)


def get_user_offers(user):
    return Room.objects.filter(room_owner=user)


def get_user_current_rentals(user):
    return CurrentRentals.objects.filter(user=user)


def get_user_completed_rentals(user):
    return CompletedRentals.objects.filter(user=user)


def get_user_favorites_offers(user):
    return Favorites.objects.filter(user=user)


@login_required
@transaction.atomic
def change_ad(request, pk):
    this_room = get_object_or_404(Room, pk=pk)

    this_conv_room = ConvenienceRoom.objects.filter(room_id=this_room.pk)
    this_conv = []
    for conv in this_conv_room:
        conv_el = get_object_or_404(Convenience, pk=conv.convenience_id)
        conv_id = conv_el.pk
        this_conv.append(conv_id)

    this_adr_room = get_object_or_404(Address, pk=this_room.address.pk)
    this_address = f'{this_adr_room.city}, {this_adr_room.street}, {this_adr_room.building}'

    this_image_room = OfferImages.objects.filter(room=this_room).values()
    this_image = []
    for i in this_image_room:
        this_image.append(i['image'])

    if request.method == 'POST':
        form = CreateAdForm(data=request.POST, files=request.FILES, instance=this_room)
        image_form = ImageForm(data=request.POST, files=request.FILES)
        if form.is_valid() and image_form.is_valid():
            try:
                address = check_address(form.cleaned_data['address'])
                room = form.save(commit=False)
                room.room_owner = request.user
                address.save()
                room.address = address
                room.save()
                this_adr_room.delete()

                selected_amenities = set(
                    filter(lambda it: len(it) > 0, form.cleaned_data['selected_amenities'].split(',')))
                for conv in this_conv_room:
                    conv.delete()
                con_list = []
                for amenity_id in selected_amenities:
                    c_room = ConvenienceRoom()
                    c_room.room_id = room.pk
                    c_room.convenience_id = amenity_id
                    con_list.append(c_room)

                ConvenienceRoom.objects.bulk_create(con_list)
                if request.FILES:
                    images = OfferImages.objects.filter(room=this_room)
                    for image in images:
                        image.delete()

                for image in image_form.files.getlist('image'):
                    OfferImages.objects.create(room=room, image=ContentFile(image.read(), image.name))

            except ValidationError as e:
                form.add_error('address', e)
            return HttpResponseRedirect(reverse('user:locations'))
    else:
        form = CreateAdForm(instance=this_room, initial={'address': this_address})
        conv_types = []
        conveniences = list(Convenience.objects.all())
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
        'title': 'Обновить объявление',
        'form': form,
        'conv_types': conv_types,
        'conveniences': conveniences,
        'this_conv': this_conv,
        'this_address': this_address,
        'this_image': this_image
    }
    return render(request, 'userapp/change/change-location.html', context)


@login_required
def booking_history(request):
    title = 'Админка - Истории бронирований'
    if request.method == 'POST':
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        user_booking = CurrentRentals.objects.filter(offer__room_owner=request.user).filter(
            start_date__range=[start, end]).filter(
            end_date__range=[start, end])
        user_booking_completed = CompletedRentals.objects.filter(offer__room_owner=request.user).filter(
            start_date__range=[start, end]).filter(
            end_date__range=[start, end])
    else:
        user_booking = CurrentRentals.objects.filter(offer__room_owner=request.user)
        user_booking_completed = CompletedRentals.objects.filter(offer__room_owner=request.user)
    context = {
        'title': title,
        'user_booking': user_booking,
        'user_booking_completed': user_booking_completed
    }
    return render(request, 'userapp/booking-history.html', context)


@login_required
def user_profile(request):
    title = 'ЛОКАЦИЯ | Профиль пользователя'
    if request.method == 'POST' and 'change_data' in request.POST:
        data_form = UserForm(request.POST, request.FILES, instance=request.user)
        if data_form.is_valid():
            data_form.save()

            return HttpResponseRedirect(reverse('user:profile'))
        else:
            return HttpResponseRedirect(reverse('user:profile'))
    else:
        data_form = UserForm(instance=request.user)

    if request.method == 'POST' and 'change_password' in request.POST:
        passwd_form = PasswordChangeCustomForm(request.user, request.POST)

        if passwd_form.is_valid():
            user = passwd_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _('Ваш пароль был успешно обновлен!'))
            print(messages.success)
        else:
            messages.error(request, _('Введенный пароль неверный.\n '
                                      'Новый пароль должен состоять из 8 элементов, включая латинские буквы в верхнем и нижнем регистре.'))

    else:
        passwd_form = PasswordChangeCustomForm(request.user, request.GET)

    context = {
        'title': title,
        'data_form': data_form,
        'passwd_form': passwd_form
    }
    return render(request, 'userapp/user-profile.html', context)


@login_required
def user_bookings(request):
    title = 'ЛОКАЦИЯ | Мои бронирования'
    current_rentals_dict = {}
    for rental in get_user_current_rentals(user=request.user):
        rental_images = OfferImages.objects.filter(room=rental.offer)
        current_rentals_dict[rental] = rental_images

    completed_rentals_dict = {}
    for rental in get_user_completed_rentals(user=request.user):
        rental_images = OfferImages.objects.filter(room=rental.offer)
        completed_rentals_dict[rental] = rental_images

    context = {
        'title': title,
        'current_rentals_dict': current_rentals_dict,
        'completed_rentals_dict': completed_rentals_dict,
    }
    return render(request, 'userapp/user-bookings.html', context)


@login_required
def user_locations(request):
    title = 'ЛОКАЦИЯ | Мои локации'
    offers_dict = {}
    for offer in get_user_offers(user=request.user):
        offer_images = OfferImages.objects.filter(room=offer)
        offers_dict[offer] = offer_images
    context = {
        'title': title,
        'offers_dict': offers_dict
    }
    return render(request, 'userapp/user-locations.html', context)


@login_required
def user_favorites(request):
    title = 'ЛОКАЦИЯ | Избранное'
    favorites_dict = {}
    for favorite in get_user_favorites_offers(user=request.user):
        favorite_images = OfferImages.objects.filter(room=favorite.offer)
        favorites_dict[favorite] = favorite_images
    context = {
        'title': title,
        'favorites_dict': favorites_dict,
    }
    return render(request, 'userapp/user-favorites.html', context)


@login_required
def claim_landlord(request):
    title = 'Арендодателям'
    if request.method == 'POST':
        landlord_form = LandlordApplicationForm(request.POST)
        if landlord_form.is_valid():
            user = request.user
            new_claim = Claim()
            new_claim.user_id = user
            new_claim.text = landlord_form.cleaned_data['text']
            new_claim.save()
            return HttpResponseRedirect(reverse('user:main'))
        else:
            return HttpResponseRedirect(reverse('user:main'))
    else:
        landlord_form = LandlordApplicationForm()
    context = {
        'title': title,
        'landlord_form': landlord_form
    }
    return render(request, 'userapp/landlord-application.html', context)
