from django import forms
from django.forms import ModelForm

from createapp.models import Room, RoomCategory, Address


class CreateSearchForm(ModelForm):
    name = forms.CharField(label="Наименование помещения",
                           initial='Room Name',
                           widget=forms.TextInput(attrs={'class': 'form-control py-2',
                                                         'placeholder': 'Наименование помещения'}))
    square = forms.FloatField(label="Площадь помещения",
                              initial=70,
                              widget=forms.TextInput(attrs={'placeholder': 'Площадь помещения'}))
    description = forms.CharField(label="Описание",
                                  initial="Description",
                                  widget=forms.Textarea(attrs={'class': 'form-control',
                                                               'placeholder': 'Описание',
                                                               'rows': 6}))

    payment_per_hour = forms.DecimalField(max_digits=10, initial=1000, decimal_places=2, label="Цена за час (руб.)",
                                          widget=forms.TextInput(attrs={'placeholder': 'Цена в час'}))

    category = forms.ModelChoiceField(label="Категория", queryset=RoomCategory.objects.all(),
                                      empty_label="Категория не выбрана")

    address = forms.CharField(label="Название помещения",
                              widget=forms.TextInput(
                                  attrs={'id': 'address', 'placeholder': 'Введите адрес', 'style': 'width: 100%'}))

    class Meta:
        model = Room
        fields = ['name', 'square', 'description', 'payment_per_hour', 'category', 'phone_number']
