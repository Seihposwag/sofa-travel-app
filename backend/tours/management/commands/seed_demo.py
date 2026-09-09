"""
Команда наполнения базы демонстрационными данными.

Создаёт направления, туристические предложения, тестового пользователя
и отзывы, чтобы каталог и пагинация были видны сразу после установки.

Запуск: python manage.py seed_demo
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from tours.models import Country, Review, Tour

User = get_user_model()

COUNTRIES = [
    ("Япония", "Острова контрастов: древние храмы Киото и неоновые кварталы Токио."),
    ("Франция", "Классические маршруты по Парижу, Провансу и замкам Луары."),
    ("Индонезия", "Бали, Ломбок и Комодо — океан, вулканы и рисовые террасы."),
    ("Мальдивы", "Атоллы с бунгало над водой и лучшим в мире снорклингом."),
    ("Италия", "Рим, Флоренция и Амальфитанское побережье в одном маршруте."),
    ("Турция", "Каппадокия, Памуккале и курорты Эгейского моря."),
]

TOURS = [
    ("Осенний Токио и Киото", "Япония", 189000, 10,
     "Десять дней между двумя столицами: небоскрёбы Синдзюку, рынок Цукидзи, "
     "бамбуковая роща Арасияма и клёны Киото в сезон момидзи. Перелёт, отели "
     "четыре звезды, внутренние переезды на синкансене и русскоговорящий гид."),
    ("Париж за выходные", "Франция", 64000, 4,
     "Короткая поездка для первого знакомства с городом: Лувр, Монмартр, "
     "прогулка по Сене и ужин в Латинском квартале. Отель в центре, "
     "трансферы и музейная карта включены."),
    ("Замки Луары на автомобиле", "Франция", 98000, 7,
     "Автомобильный маршрут по долине Луары с ночёвками в небольших отелях: Шамбор, "
     "Шенонсо, Амбуаз и дегустации местных вин."),
    ("Бали: океан и вулканы", "Индонезия", 142000, 12,
     "Двенадцать дней на острове: серфинг в Чангу, рассвет на вулкане Батур, "
     "водопады Гитгит и рисовые террасы Тегаллаланг. Вилла с бассейном "
     "и завтраками, аренда скутера."),
    ("Мальдивы: неделя на атолле", "Мальдивы", 265000, 8,
     "Бунгало над водой на атолле Баа, снорклинг с рифовыми акулами, "
     "закатный круиз и спа-программа. Питание по системе всё включено, "
     "перелёт гидросамолётом."),
    ("Рим и Флоренция", "Италия", 87000, 6,
     "Классический маршрут по двум городам: Колизей, Ватикан, галерея Уффици "
     "и купол Брунеллески. Переезд поездом, отели рядом с историческим центром."),
    ("Амальфитанское побережье", "Италия", 112000, 9,
     "Позитано, Амальфи и Равелло, прогулка по Тропе богов, катер до Капри "
     "и кулинарный мастер-класс с видом на море."),
    ("Каппадокия и Памуккале", "Турция", 71000, 7,
     "Полёт на воздушном шаре над долиной Гёреме, подземные города, "
     "белые террасы Памуккале и античный Иераполис."),
]

REVIEWS = [
    "Всё прошло идеально: трансферы вовремя, отель в шаге от центра. Гид отвечал даже на вопросы вне программы.",
    "Программа насыщенная, но не изматывающая — свободного времени хватало и на себя.",
    "Соотношение цены и качества лучшее из того, что мы смотрели. Поедем ещё раз.",
]


class Command(BaseCommand):
    help = "Наполняет базу демонстрационными направлениями, турами и отзывами"

    @transaction.atomic
    def handle(self, *args, **options):
        manager, created = User.objects.get_or_create(
            username="manager",
            defaults={
                "email": "manager@travelworld.ru",
                "first_name": "Софья",
                "last_name": "Светлакова",
                "bio": "Менеджер бюро путешествий «Travel World».",
            },
        )
        if created:
            manager.set_password("travel2026")
            manager.save()
            self.stdout.write("Создан пользователь manager с паролем travel2026")

        guest, created = User.objects.get_or_create(
            username="traveller",
            defaults={"email": "traveller@example.com", "first_name": "Иван"},
        )
        if created:
            guest.set_password("travel2026")
            guest.save()
            self.stdout.write("Создан пользователь traveller с паролем travel2026")

        countries = {}
        for title, description in COUNTRIES:
            country, _ = Country.objects.get_or_create(
                title=title,
                defaults={"description": description},
            )
            countries[title] = country

        created_tours = 0
        for title, country_title, price, days, description in TOURS:
            tour, was_created = Tour.objects.get_or_create(
                title=title,
                defaults={
                    "country": countries[country_title],
                    "price": Decimal(price),
                    "duration_days": days,
                    "description": description,
                    "author": manager,
                },
            )
            if was_created:
                created_tours += 1
                for index, text in enumerate(REVIEWS[: (tour.pk % 3) + 1]):
                    Review.objects.create(
                        tour=tour,
                        author=guest if index % 2 == 0 else manager,
                        text=text,
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: направлений {Country.objects.count()}, "
                f"туров {Tour.objects.count()} (добавлено {created_tours}), "
                f"отзывов {Review.objects.count()}"
            )
        )
