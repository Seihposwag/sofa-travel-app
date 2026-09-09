# Заполнение базы тестовыми данными: python manage.py seed_demo

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from tours.models import Country, Review, Tour

User = get_user_model()

COUNTRIES = [
    ("Япония", "Храмы Киото и неоновые кварталы Токио."),
    ("Франция", "Париж, Прованс и замки Луары."),
    ("Индонезия", "Бали и Ломбок: океан, вулканы, рисовые террасы."),
    ("Мальдивы", "Атоллы, бунгало над водой и снорклинг."),
    ("Италия", "Рим, Флоренция и Амальфитанское побережье."),
    ("Турция", "Каппадокия, Памуккале и курорты Эгейского моря."),
]

TOURS = [
    ("Токио и Киото", "Япония", 189000, 10,
     "Две столицы за одну поездку: Синдзюку, рынок Цукидзи, бамбуковая роща "
     "Арасияма и клёны Киото. Перелёт, отели 4 звезды, переезды на синкансене."),
    ("Париж за выходные", "Франция", 64000, 4,
     "Короткая поездка для первого знакомства: Лувр, Монмартр, прогулка по Сене. "
     "Отель в центре, трансферы и музейная карта включены."),
    ("Замки Луары", "Франция", 98000, 7,
     "Автомобильный маршрут по долине Луары: Шамбор, Шенонсо, Амбуаз "
     "и дегустация местных вин."),
    ("Бали: океан и вулканы", "Индонезия", 142000, 12,
     "Серфинг в Чангу, рассвет на вулкане Батур, водопады Гитгит. "
     "Вилла с бассейном, завтраки, аренда скутера."),
    ("Неделя на атолле", "Мальдивы", 265000, 8,
     "Бунгало над водой, снорклинг с рифовыми акулами, закатный круиз. "
     "Всё включено, перелёт гидросамолётом."),
    ("Рим и Флоренция", "Италия", 87000, 6,
     "Колизей, Ватикан, галерея Уффици и купол Брунеллески. "
     "Переезд поездом, отели рядом с центром."),
    ("Амальфитанское побережье", "Италия", 112000, 9,
     "Позитано, Амальфи и Равелло, Тропа богов, катер до Капри."),
    ("Каппадокия и Памуккале", "Турция", 71000, 7,
     "Полёт на воздушном шаре над Гёреме, подземные города, белые террасы."),
]

REVIEWS = [
    "Всё прошло без задержек, отель в шаге от центра. Гид отвечал на любые вопросы.",
    "Программа насыщенная, но свободное время оставалось.",
    "По цене и качеству лучший вариант из тех, что смотрели.",
]


class Command(BaseCommand):
    help = "Заполняет базу тестовыми направлениями, турами и отзывами"

    def handle(self, *args, **options):
        # администратор для входа в админку
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@travelworld.ru",
                password="travel2026",
            )

        manager, created = User.objects.get_or_create(
            username="manager",
            defaults={"email": "manager@travelworld.ru", "first_name": "Софья"},
        )
        if created:
            manager.set_password("travel2026")
            manager.save()

        traveller, created = User.objects.get_or_create(
            username="traveller",
            defaults={"email": "traveller@example.com", "first_name": "Иван"},
        )
        if created:
            traveller.set_password("travel2026")
            traveller.save()

        countries = {}
        for title, description in COUNTRIES:
            country, _ = Country.objects.get_or_create(
                title=title,
                defaults={"description": description},
            )
            countries[title] = country

        for title, country_title, price, days, description in TOURS:
            tour, created = Tour.objects.get_or_create(
                title=title,
                defaults={
                    "country": countries[country_title],
                    "price": price,
                    "duration_days": days,
                    "description": description,
                    "author": manager,
                },
            )
            if created:
                for text in REVIEWS[:2]:
                    Review.objects.create(tour=tour, author=traveller, text=text)

        self.stdout.write("Направлений: %d, туров: %d, отзывов: %d" % (
            Country.objects.count(),
            Tour.objects.count(),
            Review.objects.count(),
        ))
