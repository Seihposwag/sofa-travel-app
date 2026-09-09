# Доменная модель. Диаграмма классов

Проект: веб-приложение «Бюро путешествий» (Travel World)

---

## Диаграмма

```mermaid
classDiagram
    class User {
        +int id
        +str username
        +str email
        +str password
        +str first_name
        +str last_name
        +bool is_staff
        +bool is_active
        +str bio
        +ImageField avatar
        +str phone
        +__str__()
    }

    class Country {
        +int id
        +str title
        +str description
        +datetime created_at
        +__str__()
        +get_absolute_url()
    }

    class Tour {
        +int id
        +str title
        +str description
        +Decimal price
        +int duration_days
        +ImageField photo
        +datetime created_at
        +datetime updated_at
        +bool is_published
        +int views
        +__str__()
        +get_absolute_url()
    }

    class Review {
        +int id
        +str text
        +datetime created_at
        +bool is_active
        +__str__()
    }

    class Favorite {
        +int id
        +datetime created_at
        +__str__()
    }

    Country "1" --> "0..*" Tour : направление
    User "1" --> "0..*" Tour : автор
    Tour "1" --> "0..*" Review : отзывы
    User "1" --> "0..*" Review : автор отзыва
    User "1" --> "0..*" Favorite : избранное
    Tour "1" --> "0..*" Favorite : в избранном
```

## Сущности

| Класс | Что описывает | Приложение |
|---|---|---|
| `User` | Пользователь сайта. Наследуется от `AbstractUser`, добавлены `bio`, `avatar`, `phone` | `users` |
| `Country` | Направление путешествия, играет роль категории | `tours` |
| `Tour` | Туристическое предложение — основная сущность | `tours` |
| `Review` | Отзыв пользователя о туре | `tours` |
| `Favorite` | Отметка «в избранном» для пары пользователь–тур | `tours` |

## Связи

| Связь | Тип | Поведение при удалении |
|---|---|---|
| `Country` → `Tour` | один ко многим | `PROTECT` — направление с турами удалить нельзя |
| `User` → `Tour` | один ко многим | `SET_NULL` — при удалении автора тур остаётся без автора |
| `Tour` → `Review` | один ко многим | `CASCADE` — вместе с туром удаляются его отзывы |
| `User` → `Review` | один ко многим | `CASCADE` |
| `User` → `Favorite` | один ко многим | `CASCADE` |
| `Tour` → `Favorite` | один ко многим | `CASCADE` |

## Бизнес-правила

1. Цена тура должна быть больше нуля — проверяется в `TourForm.clean_price`.
2. Отзыв не короче 10 символов — проверяется в `ReviewForm.clean_text`.
3. Один пользователь не может добавить один тур в избранное дважды — ограничение `unique_together` в модели `Favorite`.
4. Электронная почта уникальна для всех пользователей.
5. Редактировать и удалять тур может только его автор либо администратор.
6. В каталоге показываются только туры с признаком `is_published`. Автор видит и свои неопубликованные.
7. Каждое открытие страницы тура увеличивает счётчик `views` на единицу.
