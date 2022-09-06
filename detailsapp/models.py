from django.db import models
from createapp.models import Room
from userapp.models import UserModel


class RatingNames(models.Model):
    name = models.CharField(max_length=256, verbose_name='Наименование критерия')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания записи')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления записи')


class OffersRatings(models.Model):
    offer = models.ForeignKey(Room, on_delete=models.CASCADE)
    summary_rating = models.FloatField(verbose_name='Суммарная оценка')
    reviews_number = models.PositiveIntegerField(verbose_name='Количество отзывов')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания записи')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления записи')


class CurrentRentals(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    offer = models.ForeignKey(Room, on_delete=models.CASCADE)
    seats = models.PositiveIntegerField(verbose_name='Выбранное кол-во мест')
    start_date = models.DateTimeField(verbose_name='Дата и время начала аренды')
    end_date = models.DateTimeField(verbose_name='Дата и время конца аренды')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма к оплате')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания записи')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления записи')


class CompletedRentals(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    offer = models.ForeignKey(Room, on_delete=models.CASCADE)
    seats = models.PositiveIntegerField(verbose_name='Выбранное кол-во мест')
    start_date = models.DateTimeField(verbose_name='Дата и время начала аренды')
    end_date = models.DateTimeField(verbose_name='Дата и время конца аренды')
    amount = models.PositiveIntegerField(verbose_name='Сумма к оплате')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания записи')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления записи')


class Favorites(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    offer = models.ForeignKey(Room, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания записи')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления записи')


class Rating(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    offer = models.ForeignKey(Room, on_delete=models.CASCADE)
    review_text = models.TextField(blank=False, verbose_name='Отзыв')
    summary_evaluation = models.FloatField(verbose_name='Суммарная оценка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания записи')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления записи')


class Evaluations(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    offer = models.ForeignKey(Room, on_delete=models.CASCADE)
    rating_name = models.ForeignKey(RatingNames, on_delete=models.CASCADE, verbose_name='Название')
    evaluation = models.PositiveIntegerField(verbose_name='Оценка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания записи')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления записи')
