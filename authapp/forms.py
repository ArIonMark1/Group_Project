from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
import hashlib
import random
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from userapp.models import UserModel


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserModel
        fields = 'username', 'password',


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}))
    city = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Город'}))
    email = forms.CharField(widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email'}))
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Логин'}))
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Повторите пароль'}))

    class Meta:
        model = UserModel
        fields = 'first_name', 'city', 'email', 'username', 'password1', 'password2'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        new = UserModel.objects.filter(username=username)
        if new.count():
            raise ValidationError('Пользователь с таким логином уже существует.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        new = UserModel.objects.filter(email=email)
        if new.count():
            raise ValidationError('Такой Емейл адрес уже зарегистрирован на сайте.')
        return email


class LandlordRegisterForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}))
    last_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Ваша фамилия'}))
    city = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Город'}))
    about = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'О себе', 'rows': 4}))
    email = forms.CharField(widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email'}))
    phoneNumberRegex = RegexValidator(regex=r"^\+?1?\d{8,15}$")
    user_phone = forms.CharField(min_length=10,
                                 validators=[phoneNumberRegex],
                                 widget=forms.TextInput(attrs={'class': 'form-control',
                                                               'placeholder': 'Номер телефона'}))
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Логин'}))
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Повторите пароль'}))
    is_landlord = forms.BooleanField(initial=True)

    class Meta:
        model = UserModel
        fields = 'first_name', 'last_name', 'city', 'about', 'email', 'user_phone', 'username', 'password1', 'password2', "is_landlord"

    def clean_username(self):
        username = self.cleaned_data.get('username')
        new = UserModel.objects.filter(username=username)
        if new.count():
            raise ValidationError('Пользователь с таким логином уже существует.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        new = UserModel.objects.filter(email=email)
        if new.count():
            raise ValidationError('Такой Емейл адрес уже зарегистрирован на сайте.')
        return email

    def save(self, commit=True):
        user = super(LandlordRegisterForm, self).save()
        user.is_active = False
        # ------------------------------------------
        salt = hashlib.sha256(str(random.random()).encode('utf8')).hexdigest()[:6]
        user.activation_key = hashlib.sha256((user.email + salt).encode('utf8')).hexdigest()
        # ------------------------------------------
        user.save()
        return user
