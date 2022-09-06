import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .forms import CreateAdForm, ImageForm
from .geo_checker import check_address
from .models import OfferImages, ConvenienceType, Convenience, ConvenienceRoom


@login_required
@transaction.atomic
def add_ad(request):
    if request.method == 'POST':
        form = CreateAdForm(data=request.POST, files=request.FILES)
        image_form = ImageForm(data=request.POST, files=request.FILES)
        if form.is_valid() and image_form.is_valid():
            try:
                address = check_address(form.cleaned_data['address'])
                room = form.save(commit=False)
                room.room_owner = request.user
                address.save()
                room.address = address
                room.save()

                selected_amenities = set(
                    filter(lambda it: len(it) > 0, form.cleaned_data['selected_amenities'].split(',')))

                con_list = []
                for amenity_id in selected_amenities:
                    c_room = ConvenienceRoom()
                    c_room.room_id = room.pk
                    c_room.convenience_id = amenity_id
                    con_list.append(c_room)

                ConvenienceRoom.objects.bulk_create(con_list)

                for image in image_form.files.getlist('image'):
                    OfferImages.objects.create(room=room, image=ContentFile(image.read(), image.name))

            except ValidationError as e:
                form.add_error('address', e)
            return HttpResponseRedirect(reverse('user:profile'))
    else:
        form = CreateAdForm()
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
        'title': 'Добавить новое объявление',
        'form': form,
        'conv_types': conv_types,
        'conveniences': conveniences
    }
    return render(request, 'createapp/advertisement.html', context)


def read_template(file_name):
    with open(os.path.join(settings.BASE_DIR,
                           'createapp', 'templates', 'createapp', 'includes', 'amenities', file_name), 'r') as file:
        return file.read().rstrip()
