from django.forms import ModelForm, CharField, PasswordInput, ClearableFileInput
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, PasswordChangeForm
from userapp.models import UserModel
from adminapp.models import Claim
from django.core.exceptions import ValidationError
from createapp.models import Room, RoomCategory
from django.core.validators import RegexValidator


# from phonenumber_field.formfields import PhoneNumberField

class UserForm(ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(
        attrs={'type': "text", 'name': "first_name", 'class': "form-control", 'id': "firstName"}))
    last_name = forms.CharField(widget=forms.TextInput(
        attrs={'type': "text", 'name': "last_name", 'class': "form-control", 'id': "lastName"}))
    about = forms.CharField(widget=forms.Textarea(
        attrs={'class': "form-control", 'name': "about", 'id': "about", 'style': "height: 100px"}))
    city = forms.CharField(widget=forms.TextInput(
        attrs={'type': "text", 'name': "city", 'class': "form-control", 'id': "city"}))
    user_phone = forms.CharField(widget=forms.TextInput(
        attrs={'type': "text", 'name': "user_phone", 'class': "form-control", 'id': "user_phone"}))
    email = forms.CharField(widget=forms.TextInput(
        attrs={'type': "text", 'name': "email", 'class': "form-control", 'id': "email"}))
    avatar = forms.ImageField(required=False, widget=ClearableFileInput(
        attrs={'class': 'form-control', 'name': "avatar", 'id': 'formFile'}))

    class Meta:
        model = UserModel
        fields = (
            'first_name', 'last_name',
            'city', 'user_phone', 'email',
            'avatar', 'about')

    # def __int__(self, *args, **kwargs):
    #     super(UserForm, self).__int__(*args, **kwargs)
    #
    #     for field_name, field in self.fields.items():
    #         field.widget.attrs['class'] = 'form-control'


class PasswordChangeCustomForm(PasswordChangeForm):
    error_css_class = 'has-error'

    error_messages = {'password_incorrect':
                          "Password incorrect. Please try again."}

    old_password = CharField(required=True, label='Старый пароль', widget=PasswordInput(
        attrs={'class': 'form-control'}),
                             error_messages={'required': 'Неверно введен пароль.'})

    new_password1 = CharField(required=True, label='Новый пароль',
                              widget=PasswordInput(attrs={'class': 'form-control'}),
                              error_messages={
                                  'required': 'Пароль не соответствует стандартам. Используйте цифры и латинские буквы разных регистров.'})
    new_password2 = CharField(required=True, label='Повторите новый пароль',
                              widget=PasswordInput(attrs={'class': 'form-control'}),
                              error_messages={
                                  'required': 'Пароли не совпадают. Попробуйте еще раз'})

    def clean_new_password2(self):

        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    'Пароли не совпадают! '
                    'Пожалуйста введите новый пароль и повторите его для подтверждения.'
                )
        return password2


class LandlordApplicationForm(ModelForm):
    text = forms.CharField(widget=forms.Textarea(
        attrs={'class': "form-control", 'id': "inputText", 'name': "text", 'rows': "10"}))

    class Meta:
        model = Claim
        fields = ['text']


class CreateAdForm(ModelForm):
    name = forms.CharField(label="Наименование помещения",
                           initial='Room Name',
                           widget=forms.TextInput(attrs={'style': 'width:100%', 'class': 'form-input',
                                                         'placeholder': 'Наименование помещения'}))
    square = forms.FloatField(label="Площадь помещения",
                              initial=70,
                              widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Площадь помещения'}))
    description = forms.CharField(label="Описание",
                                  initial="Description",
                                  widget=forms.Textarea(attrs={'class': 'form-control form-input',
                                                               'placeholder': 'Описание',
                                                               'rows': 4}))

    payment_per_hour = forms.DecimalField(max_digits=10, initial=1000, decimal_places=2, label="Цена за час (руб.)",
                                          widget=forms.TextInput(attrs={'class': 'form-input',
                                                                        'placeholder': 'Цена в час'}))
    category = forms.ModelChoiceField(label="Категория", queryset=RoomCategory.objects.all(),
                                      empty_label="Выберите категорию",
                                      widget=forms.Select(attrs={'class': 'form-input'}))
    seats_number = forms.IntegerField(initial=1000, label="Количество рабочих мест", widget=forms.TextInput(attrs={
        'class': 'form-input'}))
    minimum_booking_time = forms.IntegerField(initial=70, label="Минимальное время аренды",
                                              widget=forms.TextInput(attrs={
                                                  'class': 'form-input'}))
    start_working_hours = forms.TimeField(initial='8:00', label="Время работы помещения с ",
                                          widget=forms.TextInput(attrs={
                                              'class': 'form-input', 'placeholder': 'чч:мм'}))
    end_working_hours = forms.TimeField(initial='23:00', label="Время завершения работы помещения до ",
                                        widget=forms.TextInput(attrs={
                                            'class': 'form-input', 'placeholder': 'чч:мм'}))
    phoneNumberRegex = RegexValidator(regex=r"^\+?1?\d{8,15}$")
    phone_number = forms.CharField(min_length=10, initial=89995555555,
                                   validators=[phoneNumberRegex],
                                   widget=forms.TextInput(attrs={'class': 'form-input',
                                                                 'placeholder': 'Номер телефона'}))
    address = forms.CharField(label="Название помещения",
                              min_length=7,
                              widget=forms.TextInput(attrs={'id': 'address', 'class': 'form-input',
                                                            'placeholder': 'Введите адрес',
                                                            'style': 'width: 100%'}))

    image = forms.ImageField(required=False, label="Фото", widget=ClearableFileInput(
        attrs={'class': 'file-input', 'onChange': 'onFileUpload(event)'}))

    selected_amenities = forms.CharField(required=False, widget=forms.HiddenInput())

    # email = forms.CharField(widget=forms.EmailInput(attrs={
    #     'class': 'form-control py-4', 'placeholder': 'Input user\' email'}))

    class Meta:
        model = Room
        fields = ['name', 'square', 'description', 'payment_per_hour', 'category', 'seats_number',
                  'minimum_booking_time', 'start_working_hours', 'end_working_hours', 'phone_number']