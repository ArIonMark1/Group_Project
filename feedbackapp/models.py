from django.db import models
from django.shortcuts import reverse


class Contact(models.Model):
    first_address = models.TextField(
        verbose_name='Первый адрес',
        blank=False
    )

    second_address = models.TextField(
        verbose_name='Второй адрес',
        blank=False
    )

    first_phone = models.CharField(
        verbose_name='Первый телефон',
        max_length=20,
        blank=False
    )

    second_phone = models.CharField(
        verbose_name='Второй телефон',
        max_length=20,
        blank=False
    )

    first_mail = models.EmailField(
        verbose_name='Первая почта',
        max_length=254,
        blank=False
    )

    second_mail = models.EmailField(
        verbose_name='Вторая почта',
        max_length=254,
        blank=False
    )

    working_days = models.CharField(
        verbose_name='Дни работы',
        max_length=128,
        blank=False
    )

    Opening_hours = models.CharField(
        verbose_name='Часы работы',
        max_length=128,
        blank=False
    )

    def __str__(self):
        return 'Контакты'

    class Meta:
        verbose_name = 'Контакты'
        verbose_name_plural = 'Контакты'


class QuestionCategory(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name='имя',
        blank=False,
        unique=True,
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    updated = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория F.A.Q.'
        verbose_name_plural = 'Категории - F.A.Q.'


class Question(models.Model):
    category = models.ForeignKey(
        QuestionCategory,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        verbose_name='имя вопроса',
        max_length=128,
        blank=False,
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name='URL'
    )

    text = models.TextField(
        verbose_name='решение проблемы',
        blank=False,
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    updated = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('feedback:question', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Вопрос - F.A.Q.'
        verbose_name_plural = 'Вопросы - F.A.Q.'


class Message(models.Model):
    name = models.CharField(
        verbose_name='имя пользователя',
        max_length=128,
        blank=False,
    )

    email = models.EmailField(
        verbose_name='почта',
        max_length=254,
        blank=False
    )

    subject = models.CharField(
        verbose_name='тема',
        max_length=255,
        blank=False
    )

    message = models.TextField(
        verbose_name='сообщение',
        blank=False,
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        verbose_name='активна',
        default=True)

    def __str__(self):
        return f"{self.name} ({self.subject})"

    class Meta:
        verbose_name = 'Сообщение от пользователя'
        verbose_name_plural = 'Сообщения от пользователей'