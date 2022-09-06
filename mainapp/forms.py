from django import forms
from django.forms import Form, TextInput


class SearchMainForm(Form):
    city = forms.CharField(label="Адрес",
                           required=True,
                           widget=TextInput(attrs={'id': 'suggest', 'class': 'form-control',
                                                   'placeholder': 'Город'}))

    date_from = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'id': 'date-from'}))
    date_to = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'id': 'date-to'}))
