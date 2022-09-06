from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from detailsapp.views import get_offer_context, RatingNames
from feedbackapp.models import *
from django.urls import reverse
from adminapp.forms import *
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from createapp.models import *
# from authapp.models import UserModel
from userapp.models import UserModel
from createapp.models import ConvenienceType, Convenience
from adminapp.models import Claim
from offersapp.views import get_offers
from detailsapp.models import CurrentRentals, CompletedRentals

from authapp.views import send_verify_mail


def check_admin(user):
    return user.is_superuser


def check_admin_staff(user):
    return user.is_staff


def add_images_info(rooms):
    offers_dict = {}
    for room in rooms:
        room_images = OfferImages.objects.filter(room=room)
        # room_images = [_ for _ in room_images]
        offers_dict[room] = room_images
    return offers_dict


# ==================================
""" НУЖНО ПИСАТЬ КОМЕНТАРИИ!!!! """


# ==================================


@user_passes_test(check_admin)
def user(request, pk):
    title = 'Админка - Пользователь'

    this_user = get_object_or_404(UserModel, pk=pk)

    context = {
        'title': title,
        'this_user': this_user
    }
    return render(request, 'adminapp/users/user.html', context)


@user_passes_test(check_admin_staff)
def booking(request):
    title = 'Админка - Истории бронирований'

    if request.method == 'POST':
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        user_booking = CurrentRentals.objects.filter(start_date__range=[start, end]).filter(
            end_date__range=[start, end])
        user_booking_completed = CompletedRentals.objects.filter(start_date__range=[start, end]).filter(
            end_date__range=[start, end])
    else:
        user_booking = CurrentRentals.objects.all()
        user_booking_completed = CompletedRentals.objects.all()
    context = {
        'title': title,
        'user_booking': user_booking,
        'user_booking_completed': user_booking_completed
    }
    return render(request, 'adminapp/offers/booking.html', context)


@user_passes_test(check_admin_staff)
def landlord_history(request, pk):
    title = 'Админка - Арендодалели'

    claim_landlord = get_object_or_404(Claim, pk=pk)
    context = {
        'title': title,
        'claim_landlord': claim_landlord
    }
    return render(request, 'adminapp/landlords/landlord-history.html', context)


@user_passes_test(check_admin_staff)
def criterion_delete(request, pk):
    criterion_item = get_object_or_404(RatingNames, pk=pk)
    criterion_item.delete()
    return HttpResponseRedirect(reverse('admin_staff:criterion'))


@user_passes_test(check_admin_staff)
def criterion_edit(request, pk):
    title = 'Админка - Критерии'
    criterion_item = get_object_or_404(RatingNames, pk=pk)
    if request.method == 'POST':
        criterion_form = CriterionEditForm(request.POST, instance=criterion_item)
        if criterion_form.is_valid():
            criterion_form.save()
            return HttpResponseRedirect(reverse('admin_staff:criterion'))
        else:
            return HttpResponseRedirect(reverse('admin_staff:criterion'))
    else:
        criterion_form = QuestionCategoryEditForm(instance=criterion_item)
    context = {
        'title': title,
        'criterion_form': criterion_form
    }
    return render(request, 'adminapp/reviews/criterion-edit.html', context)


@user_passes_test(check_admin_staff)
def criterion_add(request):
    title = 'Админка - Критерии'
    if request.method == 'POST':
        criterion_form = CriterionEditForm(request.POST)
        if criterion_form.is_valid():
            criterion_form.save()
            return HttpResponseRedirect(reverse('admin_staff:criterion'))
        else:
            return HttpResponseRedirect(reverse('admin_staff:criterion'))
    else:
        criterion_form = QuestionCategoryEditForm()
    context = {
        'title': title,
        'criterion_form': criterion_form
    }
    return render(request, 'adminapp/reviews/criterion-edit.html', context)


@user_passes_test(check_admin_staff)
def criterion(request):
    title = 'Админка - Критерии'
    criterions = RatingNames.objects.all()
    context = {
        'title': title,
        'criterions': criterions
    }
    return render(request, 'adminapp/reviews/criterion.html', context)


@user_passes_test(check_admin_staff)
def claim_accept(request, pk):
    claim_landlord = get_object_or_404(Claim, pk=pk)
    user_ll = get_object_or_404(UserModel, pk=claim_landlord.user_id.pk)
    user_ll.is_landlord = True
    user_ll.save()
    send_verify_mail(user_ll)

    claim_landlord.is_active = False
    claim_landlord.is_approved = True
    claim_landlord.save()

    return HttpResponseRedirect(reverse('admin_staff:landlords'))


@user_passes_test(check_admin_staff)
def claim_reject(request, pk):
    claim_landlord = get_object_or_404(Claim, pk=pk)
    claim_landlord.is_active = False
    claim_landlord.is_approved = False
    claim_landlord.save()
    send_verify_mail(request.user.pk)
    return HttpResponseRedirect(reverse('admin_staff:landlords'))


# ===============================================================
@user_passes_test(check_admin_staff)
def landlord(request, pk):
    title = 'Админка - Арендодалели'

    claim_landlord = get_object_or_404(Claim, pk=pk)
    context = {
        'title': title,
        'claim_landlord': claim_landlord
    }
    return render(request, 'adminapp/landlords/landlord.html', context)


@user_passes_test(check_admin_staff)
def landlords(request):
    title = 'Админка - Арендодалели'
    claim_landlords = Claim.objects.filter(is_active=True)
    context = {
        'title': title,
        'claim_landlords': claim_landlords
    }
    return render(request, 'adminapp/landlords/landlords.html', context)


@user_passes_test(check_admin_staff)
def landlords_history(request):
    title = 'Админка - Арендодалели'
    claim_landlords = Claim.objects.filter(is_active=False)
    context = {
        'title': title,
        'claim_landlords': claim_landlords
    }
    return render(request, 'adminapp/landlords/landlords-history.html', context)


# ===============================================================

@user_passes_test(check_admin_staff)
def convenience_delete(request, pk_conv, pk):
    conv = get_object_or_404(Convenience, pk=pk)
    conv.delete()
    return HttpResponseRedirect(reverse('admin_staff:convenience', kwargs={'pk': pk_conv}))


@user_passes_test(check_admin_staff)
def convenience_edit(request, pk_conv, pk):
    title = 'Админка - F.A.Q.'
    conv = get_object_or_404(Convenience, pk=pk)
    if request.method == 'POST':
        conv_form = ConvenienceEditForm(request.POST, instance=conv)
        if conv_form.is_valid():
            conv_form.save()
            return HttpResponseRedirect(reverse('admin_staff:convenience', kwargs={'pk': pk_conv}))
        else:
            return HttpResponseRedirect(reverse('admin_staff:convenience', kwargs={'pk': pk_conv}))
    else:
        conv_form = ConvenienceEditForm(instance=conv)
    context = {
        'title': title,
        'conv': conv,
        'conv_form': conv_form
    }
    return render(request, 'adminapp/offers/convenience-edit.html', context)


@user_passes_test(check_admin_staff)
def convenience_add(request, pk_conv):
    title = 'Админка - Удобства'
    conv_type = get_object_or_404(ConvenienceType, pk=pk_conv)
    if request.method == 'POST':
        conv_form = ConvenienceEditForm(request.POST)
        if conv_form.is_valid():
            new_conv = Convenience()
            new_conv.convenience_type = conv_type
            new_conv.name = conv_form.cleaned_data["name"]
            new_conv.file_name = conv_form.cleaned_data["file_name"]
            new_conv.save()
            return HttpResponseRedirect(reverse('admin_staff:convenience', kwargs={'pk': pk_conv}))
        else:
            return HttpResponseRedirect(reverse('admin_staff:convenience', kwargs={'pk': pk_conv}))
    else:
        conv_form = ConvenienceEditForm()
    context = {
        'title': title,
        'conv_type': conv_type,
        'conv_form': conv_form
    }
    return render(request, 'adminapp/offers/convenience-edit.html', context)


@user_passes_test(check_admin_staff)
def convenience(request, pk):
    title = 'Админка - F.A.Q.'
    conv_type = get_object_or_404(ConvenienceType, pk=pk)
    conveniences = Convenience.objects.filter(convenience_type_id__pk=pk)
    context = {
        'title': title,
        'conv_type': conv_type,
        'conveniences': conveniences
    }
    return render(request, 'adminapp/offers/convenience.html', context)


@user_passes_test(check_admin_staff)
def convenience_type_edit(request, pk):
    title = 'Админка - Удобства'
    conv_type = get_object_or_404(ConvenienceType, pk=pk)
    if request.method == 'POST':
        convenience_type_form = ConvenienceTypeEditForm(request.POST, instance=conv_type)
        if convenience_type_form.is_valid():
            convenience_type_form.save()
            return HttpResponseRedirect(reverse('admin_staff:convenience_type'))
        else:
            return HttpResponseRedirect(reverse('admin_staff:convenience_type'))
    else:
        convenience_type_form = ConvenienceTypeEditForm(instance=conv_type)
    context = {
        'title': title,
        'conv_type': conv_type,
        'convenience_type_form': convenience_type_form
    }
    return render(request, 'adminapp/offers/convenience-type-edit.html', context)


@user_passes_test(check_admin_staff)
def convenience_type_delete(request, pk):
    conv_type = get_object_or_404(ConvenienceType, pk=pk)
    conv_type.delete()
    return HttpResponseRedirect(reverse('admin_staff:convenience_type'))


@user_passes_test(check_admin_staff)
def convenience_type_add(request):
    title = 'Админка - Удобства'
    if request.method == 'POST':
        convenience_type_form = ConvenienceTypeEditForm(request.POST)
        if convenience_type_form.is_valid():
            convenience_type_form.save()
            return HttpResponseRedirect(reverse('admin_staff:convenience_type'))
        else:
            return HttpResponseRedirect(reverse('admin_staff:convenience_type'))
    else:
        convenience_type_form = ConvenienceTypeEditForm()
    context = {
        'title': title,
        'convenience_type_form': convenience_type_form
    }
    return render(request, 'adminapp/offers/convenience-type-edit.html', context)


@user_passes_test(check_admin)
def convenience_type(request):
    title = 'Админка - Удобства'
    convenience_types = ConvenienceType.objects.all()
    context = {
        'title': title,
        'convenience_types': convenience_types
    }
    return render(request, 'adminapp/offers/convenience-type.html', context)


@user_passes_test(check_admin)
def staff_edit(request, pk):
    user_staff = get_object_or_404(UserModel, pk=pk)
    if user_staff.is_staff is True:
        user_staff.is_staff = False
        user_staff.save()
        return HttpResponseRedirect(reverse('admin_staff:users'))
    else:
        user_staff.is_staff = True
        user_staff.save()
        return HttpResponseRedirect(reverse('admin_staff:users'))


@user_passes_test(check_admin_staff)
def room_category_delete(request, pk):
    category = get_object_or_404(RoomCategory, pk=pk)
    category.delete()
    return HttpResponseRedirect(reverse('admin_staff:room_category'))


@user_passes_test(check_admin)
def users(request):
    title = 'Админка - Категории'

    all_users = UserModel.objects.filter(is_staff=False)
    staff_users = UserModel.objects.filter(is_staff=True)

    context = {
        'title': title,
        'all_users': all_users,
        'staff_users': staff_users
    }
    return render(request, 'adminapp/users/users.html', context)


@user_passes_test(check_admin_staff)
def room_category_add(request):
    title = 'Админка - Категории'
    if request.method == 'POST':
        category_form = RoomCategoryEditForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            return HttpResponseRedirect(reverse('admin_staff:room_category'))
        else:
            return HttpResponseRedirect(reverse('admin_staff:room_category'))
    else:
        category_form = QuestionCategoryEditForm()
    context = {
        'title': title,
        'category_form': category_form
    }
    return render(request, 'adminapp/room_category/room-category-edit.html', context)


@user_passes_test(check_admin_staff)
def room_category_edit(request, pk):
    title = 'Админка - Категории'
    category = get_object_or_404(RoomCategory, pk=pk)
    if request.method == 'POST':
        category_form = RoomCategoryEditForm(request.POST, instance=category)
        if category_form.is_valid():
            category_form.save()
            return HttpResponseRedirect(reverse('admin_staff:room_category'))
        else:
            return HttpResponseRedirect(reverse('admin_staff:room_category'))
    else:
        category_form = QuestionCategoryEditForm(instance=category)
    context = {
        'title': title,
        'category': category,
        'category_form': category_form
    }
    return render(request, 'adminapp/room_category/room-category-edit.html', context)


@user_passes_test(check_admin_staff)
def room_category(request):
    title = 'Админка - Категории'

    room_category = RoomCategory.objects.all()

    context = {
        'title': title,
        'room_category': room_category
    }
    return render(request, 'adminapp/room_category/room-category.html', context)


@user_passes_test(check_admin_staff)
def allow_publishing(request, pk):
    offer = get_object_or_404(Room, pk=pk)
    if offer.is_active is True:
        offer.is_active = False
        offer.save()
        return HttpResponseRedirect(reverse('admin_staff:offers'))
    else:
        offer.is_active = True
        offer.save()
        return HttpResponseRedirect(reverse('admin_staff:pre_moderation'))


@user_passes_test(check_admin_staff)
def show_offers_details(request, pk):
    context = get_offer_context(offer=get_object_or_404(Room, pk=pk))
    return render(request, 'adminapp/offers/offers-pm-active.html', context=context)


@user_passes_test(check_admin_staff)
def pre_moderation(request):
    title = 'Админка - Заказы'

    offers_list = Room.objects.filter(is_active=False)
    offers_dict = add_images_info(offers_list)

    context = {
        'title': title,
        'offers_list': offers_list,
        'offers_dict': offers_dict,
    }
    return render(request, 'adminapp/offers/offers.html', context)


@user_passes_test(check_admin_staff)
def offers(request):
    title = 'Админка - Заказы'

    offers_list = get_offers()
    offers_dict = add_images_info(offers_list)

    context = {
        'title': title,
        'offers_list': offers_list,
        'offers_dict': offers_dict,
    }
    return render(request, 'adminapp/offers/offers.html', context)


@user_passes_test(check_admin_staff)
def main(request):
    title = 'Админка'

    context = {
        'title': title,
    }
    return render(request, 'adminapp/index.html', context)


@user_passes_test(check_admin_staff)
def edit_contacts(request):
    title = 'Админка - Контакты'
    contacts = Contact.objects.first()
    if request.method == 'POST':
        contact_form = ContactEditForm(request.POST, instance=contacts)
        if contact_form.is_valid():
            contact_form.save()
            return HttpResponseRedirect(reverse('admin_staff:contact'))
        else:
            return HttpResponseRedirect(reverse('admin_staff:contact'))
    else:
        message_form = ContactEditForm(instance=contacts)
    context = {
        'title': title,
        'contacts': contacts,
        'message_form': message_form
    }
    return render(request, 'adminapp/edit_contact.html', context)


@user_passes_test(check_admin_staff)
def question_category(request):
    title = 'Админка - F.A.Q.'

    faq_category = QuestionCategory.objects.all()

    context = {
        'title': title,
        'faq_category': faq_category
    }
    return render(request, 'adminapp/faq-category.html', context)


@user_passes_test(check_admin_staff)
def category(request, pk):
    title = 'Админка - F.A.Q.'
    category = get_object_or_404(QuestionCategory, pk=pk)
    if request.method == 'POST':
        category_form = QuestionCategoryEditForm(request.POST, instance=category)
        if category_form.is_valid():
            category_form.save()
            return HttpResponseRedirect(reverse('admin_staff:question_category'))
        else:
            return HttpResponseRedirect(reverse('admin_staff:question_category'))
    else:
        category_form = QuestionCategoryEditForm(instance=category)
    context = {
        'title': title,
        'category': category,
        'category_form': category_form
    }
    return render(request, 'adminapp/faq-category-edit.html', context)


@user_passes_test(check_admin_staff)
def add_category(request):
    title = 'Админка - F.A.Q.'
    if request.method == 'POST':
        category_form = QuestionCategoryEditForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            return HttpResponseRedirect(reverse('admin_staff:question_category'))
        else:
            return HttpResponseRedirect(reverse('admin_staff:question_category'))
    else:
        category_form = QuestionCategoryEditForm()
    context = {
        'title': title,
        'category_form': category_form
    }
    return render(request, 'adminapp/faq-category-edit.html', context)


@user_passes_test(check_admin_staff)
def delete_category(request, pk):
    category = get_object_or_404(QuestionCategory, pk=pk)
    category.delete()
    return HttpResponseRedirect(reverse('admin_staff:question_category'))


@user_passes_test(check_admin_staff)
def questions(request, pk):
    title = 'Админка - F.A.Q.'
    faq_category = get_object_or_404(QuestionCategory, pk=pk)
    faq_question = Question.objects.filter(category__pk=pk)
    context = {
        'title': title,
        'faq_category': faq_category,
        'faq_question': faq_question
    }
    return render(request, 'adminapp/faq-questions.html', context)


@user_passes_test(check_admin_staff)
def question_edit(request, pk_cat, pk):
    title = 'Админка - F.A.Q.'
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        question_form = QuestionEditForm(request.POST, instance=question)
        if question_form.is_valid():
            question_form.save()
            return HttpResponseRedirect(reverse('admin_staff:questions', kwargs={'pk': pk_cat}))
        else:
            return HttpResponseRedirect(reverse('admin_staff:questions', kwargs={'pk': pk_cat}))
    else:
        question_form = QuestionEditForm(instance=question)
    context = {
        'title': title,
        'question': question,
        'question_form': question_form
    }
    return render(request, 'adminapp/faq-question-edit.html', context)


@user_passes_test(check_admin_staff)
def question_add(request, pk_cat):
    title = 'Админка - F.A.Q.'
    faq_category = get_object_or_404(QuestionCategory, pk=pk_cat)
    if request.method == 'POST':
        question_form = QuestionEditForm(request.POST)
        if question_form.is_valid():
            new_question = Question()
            new_question.category = faq_category
            new_question.name = question_form.cleaned_data["name"]
            new_question.slug = question_form.cleaned_data["slug"]
            new_question.text = question_form.cleaned_data["text"]
            new_question.save()
            return HttpResponseRedirect(reverse('admin_staff:questions', kwargs={'pk': pk_cat}))
        else:
            print(False)
            return HttpResponseRedirect(reverse('admin_staff:questions', kwargs={'pk': pk_cat}))
    else:
        question_form = QuestionEditForm()
    context = {
        'title': title,
        'faq_category': faq_category,
        'question_form': question_form
    }
    return render(request, 'adminapp/faq-question-edit.html', context)


@user_passes_test(check_admin_staff)
def question_delete(request, pk_cat, pk):
    question = get_object_or_404(Question, pk=pk)
    question.delete()
    return HttpResponseRedirect(reverse('admin_staff:questions', kwargs={'pk': pk_cat}))


@user_passes_test(check_admin_staff)
def message(request):
    title = 'Админка - Сообщения'

    messages_active = Message.objects.filter(is_active=True)
    messages_not_active = Message.objects.filter(is_active=False)

    context = {
        'title': title,
        'messages_active': messages_active,
        'messages_not_active': messages_not_active
    }
    return render(request, 'adminapp/messages.html', context)


@user_passes_test(check_admin_staff)
def get_message(request, pk):
    title = 'Админка - Сообщения'

    message_active = get_object_or_404(Message, pk=pk)

    context = {'title': title,
               'message_active': message_active
               }

    return render(request, 'adminapp/get-message.html', context)


@user_passes_test(check_admin_staff)
def delete_message(request, pk):
    message_active = get_object_or_404(Message, pk=pk)
    message_active.is_active = False
    message_active.save()
    return HttpResponseRedirect(reverse('admin_staff:message'))
