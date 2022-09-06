from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.utils.translation import gettext as _

from django.contrib import auth, messages
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.views.generic.edit import CreateView, UpdateView
from authapp.forms import UserRegisterForm, UserLoginForm, LandlordRegisterForm

from django.conf import settings

# ================================================================
# =========================== Login ==============================
from userapp.models import UserModel
from adminapp.models import Claim


# from adminapp.forms import ClaimForm


def login(request):
    """ Логирование пользователей с простой проверкой активности пользователя на сайте """
    title = 'Авторизация'

    if request.method == "POST":
        form = UserLoginForm(data=request.POST)

        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            # =====================
            user = auth.authenticate(request, username=username, password=password)
            if user and user.is_active:
                auth.login(request, user)
                return redirect('main')
        else:
            print('Ошибка данных!!!', form.errors)
            messages.error(request, form.errors)

    else:
        if request.user.is_active:
            return redirect('main')

        form = UserLoginForm(data=request.GET)

    context = {
        'title': title,
        'form': form,
    }
    return render(request, 'authapp/account_login.html', context)


# ================================================================
# ====================== Logout ================================
def user_logout(request):
    auth.logout(request)

    return redirect('main')


# ================================================================

def choose_type(request):
    """ Памперс """
    return render(request, 'authapp/choose_type.html')


class UserRegisterView(CreateView):
    """ Регистрация нового пользователя,
    механика активации пользователя через почту """

    model = UserModel
    form_class = UserRegisterForm
    template_name = 'authapp/user-register.html'
    success_url = reverse_lazy('auth:login')
    success_message = 'Пользователь успешно зарегистрирован.'

    def form_valid(self, form):

        if form.is_valid():

            user = form.save(commit=False)
            user.is_active = False
            user.save()
            # to get the domain of the current site
            if send_verify_mail(user):
                messages.success(self.request, _('Сообщение подтверждения регистрации отправленно на почту.'))
                print('Сообщение подтверждения регистрации отправленно на почту.')
                return redirect('auth:login')
            else:
                messages.error(self.request, _('Ошибка отправки сообщения!'))
                print('Ошибка отправки сообщения!')
                return redirect('auth:register')

        return super(UserRegisterView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(UserRegisterView, self).get_context_data(**kwargs)
        context.update({'title': 'Регистрация пользователя'})
        return context


# запилить подтверждение регистрации через админа
# !!!!!!!!!!!!!!!!!!!!!!!
# только при регистрации арендодателя не отправляем письмо на почту, а отправляем запрос(письмо) админу
# !!!!!!!!!!!!!!!!!!!!!!!
# Админ принимает решение и результат отправляет на почту
# !!!!!!!!!!!!!!!!!!!!!!!

def landlord_register(request):
    template_name = 'authapp/landlord-register.html'
    title = 'Регистрация арендодателя'

    if request.method == 'POST':
        user_form = LandlordRegisterForm(data=request.POST)
        # claim_form = ClaimForm(data=request.POST)
        if user_form.is_valid():

            user = user_form.save(commit=False)
            user.is_active = False
            # **************
            user.save()
            Claim.objects.create(user_id=user)
            # **************

            messages.success(request,
                             _('Заявка на получение прав арендодателя отправлена на рассмотрение администрации сайта.'))
            return redirect('auth:login')
        else:
            print('Error, something went unsuccessfully.')
    else:
        user_form = LandlordRegisterForm(data=request.GET)
        # claim_form = ClaimForm(data=request.GET)

    context = {'title': title, 'user_form': user_form}
    return render(request, template_name, context)


# ===================================================

# ===================================================
def verify(request, email, activation_key):
    """ Подтверждение и сохранение пользователя и его активация на сайте """

    user = UserModel.objects.filter(email=email).first()
    if user:
        if user.activation_key == activation_key and not user.is_activation_key_expired():
            user.is_active = True
            user.save()
            # auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return render(request, 'authapp/page-confirm-register.html')

    return redirect('main')


def send_verify_mail(user):
    """ Формирование шаблона письма для пользователя с ключом активации """
    subject = 'Verify your account'
    link = reverse('authapp:verify', args=[user.email, user.activation_key])
    template = render_to_string('authapp/email_template.html',
                                {'name': user.username, 'link': f"{settings.DOMAIN}{link}"})
    # функция send_mail, спецклас
    return send_mail(
        subject,  # subject
        template,  # message
        settings.EMAIL_HOST_USER,  # from_email
        [user.email],  # recipient_list - список получателей
        fail_silently=False, auth_password='zbdjzgrddsiaufqs')

    # ===================================================
# def decorator_send_email(user):

#   def send_feedback(claim_accept):

#       def wrapper_function(*args, **kwargs):
#            # логика до срабатывания функции

#           return claim_accept(*args, **kwargs)

#       # логика после срабатывания функции
#       return wrapper_function
#   return send_feedback
#
# # механизм подтверждения заявки от пользователя
#
