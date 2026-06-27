# ER-диаграмма — Модель данных Travel World SPA
> Проект: Travel World SPA | Вариант 8 — Блог о путешествиях

---

## Примечание

Проект реализован как клиентское SPA без серверной базы данных.  
ER-диаграмма описывает **логическую модель данных** приложения:
- структуры, хранимые в **localStorage**
- сущности контента, встроенные в код

---

## ER-диаграмма (localStorage + контент)

```
┌─────────────────────────────────────────┐
│           localStorage                  │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │          credentials              │  │
│  ├───────────────────────────────────┤  │
│  │  keyword       : VARCHAR(50)  NN  │  │
│  │  coupon        : VARCHAR(20)  NN  │  │
│  │  authorizedAt  : BIGINT       NN  │  │
│  └───────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│                  Контент (статический)                 │
│                                                        │
│  ┌─────────────────────────┐    ┌──────────────────┐  │
│  │   TravelDestination     │    │   TravelOffer    │  │
│  ├─────────────────────────┤    ├──────────────────┤  │
│  │ id       INT  PK        │    │ id    INT  PK    │  │
│  │ name     VARCHAR(100)   │    │ title VARCHAR    │  │
│  │ descr    TEXT           │    │ country VARCHAR  │  │
│  │ imageUrl VARCHAR(255)   │    │ duration VARCHAR │  │
│  └─────────────────────────┘    │ descr  TEXT      │  │
│                                 └──────────────────┘  │
└───────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│                  Система маршрутизации                 │
│                                                        │
│  ┌─────────────────────────┐                          │
│  │          Route          │                          │
│  ├─────────────────────────┤                          │
│  │ path     VARCHAR(50) PK │                          │
│  │ pageRef  REFERENCE      │                          │
│  │ guard    BOOLEAN        │                          │
│  └─────────────────────────┘                          │
│                                                        │
└───────────────────────────────────────────────────────┘
```

---

## Описание структуры credentials (localStorage)

| Поле | Тип | Ограничение | Пример |
|---|---|---|---|
| keyword | string | NOT NULL, min 3 символа | "TRAVEL2026" |
| coupon | string | NOT NULL, формат XX-DDDDD | "TW-45821" |
| authorizedAt | number (Unix ms) | NOT NULL | 1748000000000 |

**Ключ в localStorage:** `"credentials"`  
**Формат хранения:** JSON-строка (`JSON.stringify` / `JSON.parse`)

---

## Логические связи

| Связь | Тип | Описание |
|---|---|---|
| Route → Page | 1:1 | Каждый маршрут ссылается ровно на одну страницу |
| Route ←→ Guard | 1:0..1 | Маршрут /offers имеет guard; остальные — нет |
| credentials ↔ AuthService | — | Сервис читает/пишет единственную запись |

---

## DDL-скрипты (концептуальный уровень)

Поскольку backend отсутствует, приведены SQL-эквиваленты для демонстрации нормализации:

```sql
-- Таблица купонов (логический эквивалент)
CREATE TABLE credentials (
    id           INTEGER      PRIMARY KEY AUTOINCREMENT,
    keyword      VARCHAR(50)  NOT NULL,
    coupon       VARCHAR(20)  NOT NULL,
    authorized_at BIGINT      NOT NULL,
    CONSTRAINT uq_coupon UNIQUE (coupon)
);

-- Таблица направлений
CREATE TABLE travel_destination (
    id        INTEGER      PRIMARY KEY AUTOINCREMENT,
    name      VARCHAR(100) NOT NULL,
    descr     TEXT,
    image_url VARCHAR(255)
);

-- Таблица предложений
CREATE TABLE travel_offer (
    id       INTEGER      PRIMARY KEY AUTOINCREMENT,
    title    VARCHAR(200) NOT NULL,
    country  VARCHAR(100),
    duration VARCHAR(50),
    descr    TEXT
);

-- Таблица маршрутов (метаданные)
CREATE TABLE route (
    path      VARCHAR(50)  PRIMARY KEY,
    has_guard BOOLEAN      NOT NULL DEFAULT FALSE
);

-- Индексы
CREATE INDEX idx_credentials_coupon ON credentials(coupon);
CREATE INDEX idx_destination_name ON travel_destination(name);
```

---

## Нормализация

| Форма | Выполнение |
|---|---|
| 1НФ | Все поля атомарны, нет повторяющихся групп |
| 2НФ | Нет частичных зависимостей (все PK простые) |
| 3НФ | Нет транзитивных зависимостей между неключевыми атрибутами |
