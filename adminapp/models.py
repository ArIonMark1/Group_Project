from django.db import models
from userapp.models import UserModel
# ===================================

from django.conf import settings
from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver


class Claim(models.Model):
    user_id = models.OneToOneField(
        UserModel,
        on_delete=models.CASCADE
    )

    text = models.TextField(
        verbose_name='текст заявителя',
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        verbose_name='активна',
        default=True)

    is_approved = models.BooleanField(
        verbose_name='одобрено',
        blank=True,
        null=True)

    def __str__(self):
        return f"{self.user_id.first_name} {self.user_id.last_name}"

    class Meta:
        verbose_name = 'Заявка на получение прав арендодателя'
        verbose_name_plural = 'Заявки на получение прав арендодателя'
