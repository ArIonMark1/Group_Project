from django.core.management.base import BaseCommand
from feedbackapp.models import Contact, QuestionCategory, Question
from detailsapp.models import RatingNames
from createapp.models import ConvenienceType, Convenience, RoomCategory

contact = {
    "first_address": "A108 Adam Street,",
    "second_address": "New York, NY 535022",
    "first_phone": "+1 5589 55488 55",
    "second_phone": "+1 6678 254445 41",
    "first_mail": "info@example.com",
    "second_mail": "contact@example.com",
    "working_days": "Понедельник - Пятница",
    "Opening_hours": "9:00 - 21:00"
}
category = [
    {
        "name": "Основные"
    },
    {
        "name": "Личные данные"
    },
    {
        "name": "О сайте"
    },
]
questions = [
    {
        "category": 'Основные',
        "name": "Как связаться с тех-поддержкой?",
        "slug": "kak-svezatsa-s-teh-potdderhkoi",
        "text": "Перейдите на страницу \"Контакты\" и свяжитесь с нами через форму отправки сообщения."
    },
    {
        "category": 'Личные данные',
        "name": "Как изменить информацию о себе?",
        "slug": "kak-izmenit-informaciu-o-sebe",
        "text": "Перейдите на страницу профиля и выберете пункт \"Редактировать профиль\"."
    },
    {
        "category": 'Личные данные',
        "name": "Как сменить пароль?",
        "slug": "kak-smenit-parol",
        "text": "Перейдите на страницу профиля и выберете пункт \"Сменить пароль\"."
    },
    {
        "category": "О сайте",
        "name": "Я могу устроиться к вам работать?",
        "slug": "i-mogu-ustroitsa-k-vam-pabotat",
        "text": "Перейдите на страницу контактов и напишите нам сообщение с информацией о себе, кем вы хотите работать и прикрепите ссылку на ваше резюме. В теме сообщения напишите \"Работа\"."
    }
]
rating_names = [{'name': 'Качество помещения'}, {'name': 'Рабочая обстановка'}, {'name': 'Качество удобств'},
                {'name': 'Соответствие цена-качество'}, {'name': 'Соответствие фото'}]
convenience_types = [{'name': 'Ключевые удобства'}, {'name': 'Еда и напитки'}, {'name': 'Оборудование'},
                     {'name': 'Специальные зоны'}, {'name': 'Услуги'}, {'name': 'Общение'},
                     {'name': 'Транспорт'}, {'name': 'Здоровье'}]
conveniences = [{'name': 'Wi-Fi', 'file_name': 'wifi.html', 'convenience_type': 'Ключевые удобства'},
                {'name': 'Современный ремонт', 'file_name': 'modern_repair.html',
                 'convenience_type': 'Ключевые удобства'},
                {'name': 'Высокоскоростной интернет', 'file_name': 'high-speed_Internet.html',
                 'convenience_type': 'Ключевые удобства'},
                {'name': 'Мебель', 'file_name': 'furniture.html', 'convenience_type': 'Ключевые удобства'},
                {'name': 'Охрана', 'file_name': 'security.html', 'convenience_type': 'Ключевые удобства'},
                {'name': 'Еда и напитки', 'file_name': 'drinks.html', 'convenience_type': 'Еда и напитки'},
                {'name': 'Закуски/фрукты', 'file_name': 'snacks.html', 'convenience_type': 'Еда и напитки'},
                {'name': 'Кухня', 'file_name': 'kitchen.html', 'convenience_type': 'Еда и напитки'},
                {'name': 'Cafe', 'file_name': 'cafe.html', 'convenience_type': 'Еда и напитки'},
                {'name': 'Принтер/сканер', 'file_name': 'scanner.html', 'convenience_type': 'Оборудование'},
                {'name': 'Факс', 'file_name': 'fax.html', 'convenience_type': 'Оборудование'},
                {'name': 'Флипчарт', 'file_name': 'flipchart.html', 'convenience_type': 'Оборудование'},
                {'name': 'Переговорные комнаты', 'file_name': 'conference_room.html',
                 'convenience_type': 'Специальные зоны'},
                {'name': 'Телефон', 'file_name': 'phone.html', 'convenience_type': 'Специальные зоны'},
                {'name': 'Шкафчики', 'file_name': 'locker.html', 'convenience_type': 'Специальные зоны'},
                {'name': 'Техническая поддержка', 'file_name': 'support.html', 'convenience_type': 'Услуги'},
                {'name': 'Ресепшн', 'file_name': 'reception.html', 'convenience_type': 'Услуги'},
                {'name': 'Клининг', 'file_name': 'cleaning.html', 'convenience_type': 'Услуги'},
                {'name': 'Зоны отдыха', 'file_name': 'relax.html', 'convenience_type': 'Общение'},
                {'name': 'Мероприятия', 'file_name': 'events.html', 'convenience_type': 'Общение'},
                {'name': 'Парковка', 'file_name': 'parking.html', 'convenience_type': 'Транспорт'},
                {'name': 'Велопарковка', 'file_name': 'bike_parking.html', 'convenience_type': 'Транспорт'},
                {'name': 'Спортзал', 'file_name': 'gym.html', 'convenience_type': 'Здоровье'}]
room_categorys = [{'name': 'Open space'}, {'name': 'Office'}, {'name': 'Private office'}, {'name': 'Conference room'},
                  {'name': 'Video studio'}, ]


class Command(BaseCommand):
    def handle(self, *args, **options):
        Contact.objects.all().delete()
        new_contact = Contact(**contact)
        new_contact.save()
        QuestionCategory.objects.all().delete()
        for el in category:
            new_category = QuestionCategory(**el)
            new_category.save()
        Question.objects.all().delete()
        for question in questions:
            category_name = question['category']
            _category = QuestionCategory.objects.get(name=category_name)
            question['category'] = _category
            new_question = Question(**question)
            new_question.save()
        RatingNames.objects.all().delete()
        for rating_name in rating_names:
            new_rn = RatingNames(**rating_name)
            new_rn.save()
        ConvenienceType.objects.all().delete()
        for convenience_type in convenience_types:
            new_ct = ConvenienceType(**convenience_type)
            new_ct.save()
        Convenience.objects.all().delete()
        for convenience in conveniences:
            type_name = convenience['convenience_type']
            _type = ConvenienceType.objects.get(name=type_name)
            convenience['convenience_type'] = _type
            new_convenience = Convenience(**convenience)
            new_convenience.save()
        RoomCategory.objects.all().delete()
        for room_category in room_categorys:
            new_rc = RoomCategory(**room_category)
            new_rc.save()
