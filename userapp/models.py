from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.db import models
import pytz


class UserModel(AbstractUser):
    avatar = models.ImageField(upload_to='authapp/media/users_avatar', verbose_name='Фото профиля')
    city = models.CharField(max_length=50, verbose_name='Город')
    about = models.TextField(max_length=200, verbose_name='О себе')
    user_phone = models.CharField(max_length=15,
                                  validators=[RegexValidator(r'^\d{1,15}$')], verbose_name='Телефон')
    # ===============================================================
    email = models.EmailField(_('email address'))
    activation_key = models.CharField(max_length=255, blank=True)
    activation_key_created = models.DateTimeField(auto_now_add=True, blank=True)
    # ===============================================================
    is_landlord = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания записи')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления записи')

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def is_activation_key_expired(self):
        if datetime.now(pytz.timezone(settings.TIME_ZONE)) < (self.activation_key_created + timedelta(hours=48)):
            return False
        return True

    def save(self, *args, **kwargs):
        """On save, update timestamps """
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(UserModel, self).save(*args, **kwargs)
