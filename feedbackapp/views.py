from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from feedbackapp.models import Contact, Question, QuestionCategory, Message
from feedbackapp.forms import MessageEditForm
from django.urls import reverse
from django.contrib import messages


def main(request):
    title = 'Контакты'
    contacts = Contact.objects.first()
    if request.method == 'POST':
        message_form = MessageEditForm(request.POST)
        if message_form.is_valid():
            message_form.save()
            messages.info(request, 'Сообщение отправлено!')
            return HttpResponseRedirect(reverse('feedback:main'))
        else:
            messages.info(request, 'Сообщение НЕ отправлено!')
            return HttpResponseRedirect(reverse('feedback:main'))
    else:
        message_form = MessageEditForm()

    context = {
        'title': title,
        'contacts': contacts,
        'message_form': message_form
    }

    return render(request, 'feedbackapp/pages-contact.html', context)


def questions(request):
    title = 'F.A.Q.'
    question_category = QuestionCategory.objects.all()

    context = {
        'title': title,
        'question_category': question_category
    }
    return render(request, 'feedbackapp/pages-faq.html', context)


def question(request, slug):
    title = 'F.A.Q.'
    question = get_object_or_404(Question, slug=slug)

    context = {
        'title': title,
        'question': question
    }
    return render(request, 'feedbackapp/question.html', context)