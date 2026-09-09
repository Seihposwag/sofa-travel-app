# ER-диаграмма и модель данных

Проект: веб-приложение «Бюро путешествий» (Travel World)
СУБД: SQLite, файл `backend/db.sqlite3`

---

## ER-диаграмма

```mermaid
erDiagram
    users_user ||--o{ tours_tour : "пишет"
    users_user ||--o{ tours_review : "оставляет"
    users_user ||--o{ tours_favorite : "сохраняет"
    tours_country ||--o{ tours_tour : "содержит"
    tours_tour ||--o{ tours_review : "имеет"
    tours_tour ||--o{ tours_favorite : "попадает в"

    users_user {
        integer id PK
        varchar username UK "NOT NULL"
        varchar email UK "NOT NULL"
        varchar password "NOT NULL, хеш"
        varchar first_name
        varchar last_name
        bool is_staff "NOT NULL"
        bool is_active "NOT NULL"
        bool is_superuser "NOT NULL"
        datetime date_joined "NOT NULL"
        datetime last_login
        text bio
        varchar avatar
        varchar phone
    }

    tours_country {
        integer id PK
        varchar title UK "NOT NULL"
        text description
        datetime created_at "NOT NULL"
    }

    tours_tour {
        integer id PK
        varchar title "NOT NULL"
        text description "NOT NULL"
        decimal price "NOT NULL"
        integer duration_days "NOT NULL, CHECK >= 0"
        varchar photo
        datetime created_at "NOT NULL, индекс"
        datetime updated_at "NOT NULL"
        bool is_published "NOT NULL, индекс"
        integer views "NOT NULL, CHECK >= 0"
        bigint country_id FK "NOT NULL"
        bigint author_id FK "NULL"
    }

    tours_review {
        integer id PK
        text text "NOT NULL"
        datetime created_at "NOT NULL"
        bool is_active "NOT NULL"
        bigint tour_id FK "NOT NULL"
        bigint author_id FK "NOT NULL"
    }

    tours_favorite {
        integer id PK
        datetime created_at "NOT NULL"
        bigint user_id FK "NOT NULL"
        bigint tour_id FK "NOT NULL"
    }
```

## Связи

| Связь | Тип | Внешний ключ | При удалении |
|---|---|---|---|
| `tours_country` → `tours_tour` | 1 : N | `country_id` | `PROTECT` |
| `users_user` → `tours_tour` | 1 : N | `author_id` | `SET NULL` |
| `tours_tour` → `tours_review` | 1 : N | `tour_id` | `CASCADE` |
| `users_user` → `tours_review` | 1 : N | `author_id` | `CASCADE` |
| `users_user` → `tours_favorite` | 1 : N | `user_id` | `CASCADE` |
| `tours_tour` → `tours_favorite` | 1 : N | `tour_id` | `CASCADE` |

## Индексы

| Индекс | Таблица | Поля | Зачем |
|---|---|---|---|
| `tours_tour_created_at` | `tours_tour` | `created_at` | Сортировка каталога по дате |
| `tours_tour_is_published` | `tours_tour` | `is_published` | Отбор опубликованных туров |
| `tours_tour_country_id` | `tours_tour` | `country_id` | Фильтр по направлению |
| `tours_tour_author_id` | `tours_tour` | `author_id` | Список своих туров |
| `tours_review_tour_id` | `tours_review` | `tour_id` | Отзывы одного тура |
| `tours_favorite_user_id_tour_id_uniq` | `tours_favorite` | `user_id`, `tour_id` | Уникальность пары |

## Нормализация

| Форма | Как выполнена |
|---|---|
| 1НФ | Все поля хранят одно значение. Списков и повторяющихся групп в столбцах нет |
| 2НФ | Первичный ключ во всех таблицах простой — `id`, поэтому частичных зависимостей от части ключа быть не может |
| 3НФ | Неключевые поля не зависят друг от друга. Название направления хранится один раз в `tours_country`, тур ссылается на него через `country_id`, а не дублирует текстом |

---

## DDL-скрипты

Скрипты сняты из SQLite после применения миграций Django.

```sql
CREATE TABLE "users_user" (
    "id"           integer      NOT NULL PRIMARY KEY AUTOINCREMENT,
    "password"     varchar(128) NOT NULL,
    "last_login"   datetime     NULL,
    "is_superuser" bool         NOT NULL,
    "username"     varchar(150) NOT NULL UNIQUE,
    "first_name"   varchar(150) NOT NULL,
    "last_name"    varchar(150) NOT NULL,
    "is_staff"     bool         NOT NULL,
    "is_active"    bool         NOT NULL,
    "date_joined"  datetime     NOT NULL,
    "email"        varchar(254) NOT NULL UNIQUE,
    "bio"          text         NOT NULL,
    "avatar"       varchar(100) NULL,
    "phone"        varchar(20)  NOT NULL
);

CREATE TABLE "tours_country" (
    "id"          integer      NOT NULL PRIMARY KEY AUTOINCREMENT,
    "title"       varchar(150) NOT NULL UNIQUE,
    "description" text         NOT NULL,
    "created_at"  datetime     NOT NULL
);

CREATE TABLE "tours_tour" (
    "id"            integer          NOT NULL PRIMARY KEY AUTOINCREMENT,
    "title"         varchar(200)     NOT NULL,
    "description"   text             NOT NULL,
    "price"         decimal          NOT NULL,
    "duration_days" integer unsigned NOT NULL CHECK ("duration_days" >= 0),
    "photo"         varchar(100)     NULL,
    "created_at"    datetime         NOT NULL,
    "updated_at"    datetime         NOT NULL,
    "is_published"  bool             NOT NULL,
    "views"         integer unsigned NOT NULL CHECK ("views" >= 0),
    "author_id"     bigint           NULL REFERENCES "users_user" ("id"),
    "country_id"    bigint           NOT NULL REFERENCES "tours_country" ("id")
);

CREATE TABLE "tours_review" (
    "id"         integer  NOT NULL PRIMARY KEY AUTOINCREMENT,
    "text"       text     NOT NULL,
    "created_at" datetime NOT NULL,
    "is_active"  bool     NOT NULL,
    "author_id"  bigint   NOT NULL REFERENCES "users_user" ("id"),
    "tour_id"    bigint   NOT NULL REFERENCES "tours_tour" ("id")
);

CREATE TABLE "tours_favorite" (
    "id"         integer  NOT NULL PRIMARY KEY AUTOINCREMENT,
    "created_at" datetime NOT NULL,
    "user_id"    bigint   NOT NULL REFERENCES "users_user" ("id"),
    "tour_id"    bigint   NOT NULL REFERENCES "tours_tour" ("id")
);

CREATE INDEX "tours_tour_created_at"   ON "tours_tour" ("created_at");
CREATE INDEX "tours_tour_is_published" ON "tours_tour" ("is_published");
CREATE INDEX "tours_tour_country_id"   ON "tours_tour" ("country_id");
CREATE INDEX "tours_tour_author_id"    ON "tours_tour" ("author_id");
CREATE INDEX "tours_review_tour_id"    ON "tours_review" ("tour_id");
CREATE INDEX "tours_review_author_id"  ON "tours_review" ("author_id");
CREATE INDEX "tours_favorite_user_id"  ON "tours_favorite" ("user_id");
CREATE INDEX "tours_favorite_tour_id"  ON "tours_favorite" ("tour_id");

CREATE UNIQUE INDEX "tours_favorite_user_id_tour_id_uniq"
    ON "tours_favorite" ("user_id", "tour_id");
```
