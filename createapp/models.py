from django.db import models

from userapp.models import UserModel


class Address(models.Model):
    city = models.CharField(max_length=100, blank=False, verbose_name='Город')
    street = models.CharField(max_length=100, blank=False, verbose_name='Улица')
    building = models.CharField(max_length=20, verbose_name='Номер дома')
    latitude = models.DecimalField(max_digits=8, decimal_places=6, verbose_name='Широта')  # координато широты
    longitude = models.DecimalField(max_digits=8, decimal_places=6, verbose_name='Долгота')  # координато долготы
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания записи')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления записи')


class RoomCategory(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название категории')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания записи')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления записи')

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=256, verbose_name='Наименование помещения')
    square = models.FloatField(max_length=10, blank=False, verbose_name='Площадь помещения')
    description = models.TextField(blank=False, verbose_name='Описание')
    payment_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Оплата в час')
    category = models.ForeignKey(RoomCategory, on_delete=models.CASCADE, related_name='room_category',
                                 verbose_name='Категория')
    seats_number = models.PositiveIntegerField(verbose_name='Количество рабочих мест')
    minimum_booking_time = models.IntegerField(default=0, verbose_name='Минимальное время аренды')
    start_working_hours = models.TimeField(
        verbose_name='Время работы помещения с ')  # начало работы помещения, например, 7:00
    end_working_hours = models.TimeField(
        verbose_name='Время завершения работы помещения до ')  # закрытие помещения, например, 23:00
    phone_number = models.CharField(max_length=16, blank=False, null=False)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='room_address', verbose_name='Адрес')
    room_owner = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания записи')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления записи')
    is_active = models.BooleanField(
        verbose_name='активна',
        default=False
    )

    def __str__(self):
        return f'{self.name} | {self.category.name}'


class OfferImages(models.Model):
    room = models.ForeignKey(Room, related_name='room_images', on_delete=models.CASCADE)
    image = models.FileField(upload_to='offer_images',
                             verbose_name='Фото')  # в этом поле хранится путь в виде "offer_images/img-name.format", например: "offer_images/offer1-1.jpg"


class ConvenienceType(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name='Название категории удобств')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания записи')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления записи')


class Convenience(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name='Название удобства')
    file_name = models.CharField(max_length=64, verbose_name='Файл ресурса')
    convenience_type = models.ForeignKey(ConvenienceType, on_delete=models.CASCADE, verbose_name='Категория удобств')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания записи')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления записи')

    def __str__(self):
        return f'{self.name} | {self.convenience_type.name}'


class ConvenienceRoom(models.Model):  # здесь должен быть составной первичный ключ (room_id и convenience_id)
    room_id = models.IntegerField(
        verbose_name='id помещения')  # сюда нужно поставить тип, который джанго ставит при создании таблицы Room в колонку id
    convenience_id = models.IntegerField(
        verbose_name='id удобства')  # сюда нужно поставить тип, который джанго ставит при создании таблицы Convenience в колонку id
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания записи')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления записи')

    class Meta:
        unique_together = (('room_id', 'convenience_id'),)
