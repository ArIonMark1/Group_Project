from django import forms
from django.core.validators import RegexValidator
from django.forms import ModelForm, ClearableFileInput

from .models import Room, RoomCategory, OfferImages


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


class ImageForm(forms.ModelForm):
    image = forms.ImageField(label='Image', required=False)

    class Meta:
        model = OfferImages
        fields = ['image']
