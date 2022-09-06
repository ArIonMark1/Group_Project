from django import forms
from django.core.exceptions import ValidationError

from feedbackapp.models import Message
import re


class MessageEditForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'type': "text", 'name': "name", 'class': "form-control", 'placeholder': "Ваше имя"}))
    email = forms.CharField(widget=forms.EmailInput(
        attrs={'type': "email", 'class': "form-control", 'name': "email", 'placeholder': "Ваш Email"}))
    subject = forms.CharField(widget=forms.TextInput(
        attrs={'type': "text", 'class': "form-control", 'name': "subject", 'placeholder': "Тема"}))
    message = forms.CharField(widget=forms.Textarea(
        attrs={'class': "form-control", 'name': "message", 'rows': "6", 'placeholder': "Сообщение"}))

    class Meta:
        model = Message
        fields = 'name', 'email', 'subject', 'message'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        if re.fullmatch(regex, email):
            return email
        else:
            raise ValidationError('Инвалидный email.')
