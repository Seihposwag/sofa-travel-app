# Архитектура. Диаграмма компонентов

Проект: веб-приложение «Бюро путешествий» (Travel World)
Архитектурный стиль: Django MTV (Model — Template — View)

---

## Диаграмма компонентов

```mermaid
flowchart TB
    subgraph BROWSER["Браузер"]
        HTML["HTML-страницы"]
        JS["main.js<br/>AJAX-запросы"]
        CSS["Bootstrap 5 + main.css"]
    end

    subgraph DJANGO["Django"]
        URLS["config/urls.py<br/>tours/urls.py<br/>users/urls.py"]

        subgraph VIEWS["View — что показать"]
            TV["tours/views.py<br/>9 представлений"]
            UV["users/views.py<br/>4 представления"]
        end

        subgraph TPL["Template — как показать"]
            BASE["base.html"]
            PAGES["tours/*.html<br/>users/*.html<br/>inc/*.html"]
        end

        subgraph MODELS["Model — что хранить"]
            TM["tours/models.py<br/>Country, Tour, Review, Favorite"]
            UM["users/models.py<br/>User"]
        end

        FORMS["forms.py<br/>проверка данных"]
        ADMIN["admin.py<br/>админ-панель"]
        AUTH["Сессии Django<br/>login, logout, login_required"]
    end

    DB[("SQLite<br/>db.sqlite3")]
    MEDIA[("media/<br/>фото туров, аватары")]

    HTML --> URLS
    JS --> URLS
    CSS --- HTML

    URLS --> TV
    URLS --> UV

    TV --> FORMS
    UV --> FORMS
    FORMS --> TM
    FORMS --> UM

    TV --> TM
    UV --> UM

    TV --> PAGES
    UV --> PAGES
    PAGES --> BASE
    PAGES --> HTML

    TV -.JSON.-> JS

    TM --> DB
    UM --> DB
    ADMIN --> TM
    ADMIN --> UM
    AUTH --> UM

    TM --- MEDIA
    UM --- MEDIA
```

## Слои и ответственность

| Слой | Файлы | За что отвечает |
|---|---|---|
| Маршруты | `config/urls.py`, `tours/urls.py`, `users/urls.py` | Сопоставляет адрес и функцию-представление |
| View | `tours/views.py`, `users/views.py` | Достаёт данные, проверяет права, выбирает шаблон |
| Template | `templates/` | Формирует HTML, наследуется от `base.html` |
| Model | `tours/models.py`, `users/models.py` | Описывает таблицы, работает с базой через ORM |
| Формы | `tours/forms.py`, `users/forms.py` | Проверяет данные до записи в базу |
| Админ-панель | `admin.py` в обоих приложениях | Управление содержимым сайта |
| Аутентификация | Встроенные механизмы Django | Сессии, вход, выход, ограничение доступа |
| Статика | `static/` | Стили, скрипты, изображения |

---

## Схема взаимодействия клиент — сервер

Обычный переход по ссылке: браузер запрашивает страницу, сервер
собирает её целиком и отдаёт готовый HTML.

```mermaid
sequenceDiagram
    participant B as Браузер
    participant U as urls.py
    participant V as views.py
    participant M as models.py
    participant D as SQLite
    participant T as Шаблон

    B->>U: GET /tour/5/
    U->>V: tour_detail(request, pk=5)
    V->>M: Tour.objects.get(pk=5)
    M->>D: SELECT ... WHERE id = 5
    D-->>M: строка таблицы
    M-->>V: объект Tour
    V->>T: tour_detail.html + данные
    T-->>V: готовый HTML
    V-->>B: 200 OK, HTML-страница
```

## Схема AJAX-запроса

Отправка отзыва: страница не перезагружается, сервер отвечает JSON,
скрипт сам дописывает блок отзыва.

```mermaid
sequenceDiagram
    participant U as Пользователь
    participant JS as main.js
    participant V as views.py
    participant D as SQLite

    U->>JS: нажал «Отправить отзыв»
    JS->>JS: event.preventDefault()
    JS->>V: POST /ajax/review/5/ + csrf-токен
    V->>V: ReviewForm.is_valid()
    V->>D: INSERT INTO tours_review
    D-->>V: запись создана
    V->>V: render_to_string("inc/review.html")
    V-->>JS: JSON: ok, html, total
    JS->>U: отзыв появился, счётчик обновлён
```

## Обоснование выбора

Django выбран потому, что даёт из коробки то, что требуется по заданию:
ORM для работы с базой без ручного SQL, готовую систему пользователей
с шифрованием паролей и сессиями, автоматическую админ-панель и
шаблонизатор с наследованием. Стиль MTV разделяет данные, логику и
представление, поэтому каждый файл отвечает за одно.

База — SQLite: она входит в состав Python, не требует установки
и настройки сервера, чего достаточно для учебного проекта.
