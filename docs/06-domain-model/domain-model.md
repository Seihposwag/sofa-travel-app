# Доменная модель — Travel World SPA
> Проект: Travel World SPA | Вариант 8 — Блог о путешествиях

---

## Диаграмма классов (Domain Model)

```
┌─────────────────────────┐        ┌─────────────────────────────┐
│         Router          │        │          Page               │
├─────────────────────────┤        ├─────────────────────────────┤
│ - routes: Map           │1      *│ - path: string              │
│ - currentPage: Page     │────────│ - title: string             │
│ - currentCleanup: fn    │        │ - html: string              │
├─────────────────────────┤        │ - mountFn: function         │
│ + register(path, page)  │        ├─────────────────────────────┤
│ + render(pathname)      │        │ + mount(doc): cleanup fn    │
│ + init()                │        │ + getPath(): string         │
└──────────┬──────────────┘        │ + getTitle(): string        │
           │                       └──────────┬──────────────────┘
           │ uses                             │ implements
           ▼                                  │
┌─────────────────────────┐                   │
│      NavigateHelper     │        ┌──────────▼──────────────────┐
├─────────────────────────┤        │      CSSManager             │
│ + navigate(path): void  │        ├─────────────────────────────┤
└─────────────────────────┘        │ - currentStyleLink: Element │
                                   ├─────────────────────────────┤
                                   │ + loadStyle(cssPath): void  │
┌─────────────────────────┐        │ + removeStyle(): void       │
│      AuthService        │        └─────────────────────────────┘
├─────────────────────────┤
│ - STORAGE_KEY: string   │        ┌─────────────────────────────┐
├─────────────────────────┤        │     TravelDestination       │
│ + save(creds): void     │        ├─────────────────────────────┤
│ + get(): Credentials    │        │ - name: string              │
│ + isAuth(): boolean     │        │ - description: string       │
│ + clear(): void         │        │ - imageUrl: string          │
└─────────────────────────┘        └─────────────────────────────┘

┌─────────────────────────┐        ┌─────────────────────────────┐
│      Credentials        │        │       TravelOffer           │
├─────────────────────────┤        ├─────────────────────────────┤
│ - keyword: string       │        │ - title: string             │
│ - coupon: string        │        │ - country: string           │
│ - authorizedAt: number  │        │ - duration: string          │
└─────────────────────────┘        │ - description: string       │
                                   └─────────────────────────────┘
```

---

## Описание сущностей и атрибутов

### Router
Центральный компонент SPA. Управляет регистрацией маршрутов, рендерингом и жизненным циклом страниц.

| Атрибут/Метод | Тип | Описание |
|---|---|---|
| routes | Map\<string, Page\> | Таблица зарегистрированных маршрутов |
| currentPage | Page | Текущая активная страница |
| currentCleanup | Function | Функция очистки текущей страницы |
| register(path, page) | void | Регистрирует страницу по маршруту |
| render(pathname) | void | Монтирует страницу, вызывает unmount предыдущей |
| init() | void | Подписывается на popstate, инициирует первый рендер |

### Page
Абстракция страницы. Инкапсулирует HTML-разметку и логику жизненного цикла.

| Атрибут/Метод | Тип | Описание |
|---|---|---|
| path | string | URL-маршрут страницы (например /home) |
| title | string | Заголовок вкладки браузера |
| html | string | HTML-разметка страницы |
| mountFn | function | Функция инициализации (события, логика) |
| mount(doc) | Function | Вставляет HTML, подключает CSS, вызывает mountFn, возвращает cleanup |

### AuthService
Сервис управления клиентской авторизацией через localStorage.

| Атрибут/Метод | Тип | Описание |
|---|---|---|
| STORAGE_KEY | string | Ключ в localStorage ('credentials') |
| save(creds) | void | Сохраняет объект авторизации |
| get() | Credentials\|null | Возвращает текущую сессию |
| isAuth() | boolean | Проверяет наличие валидной сессии |
| clear() | void | Удаляет сессию из localStorage |

### Credentials
Объект авторизационных данных пользователя.

| Поле | Тип | Описание |
|---|---|---|
| keyword | string | Ключевое слово (TRAVEL2026) |
| coupon | string | Номер купона (TW-45821) |
| authorizedAt | number | Unix timestamp авторизации |

### TravelDestination
Направление путешествия (данные отображаются на главной странице).

| Поле | Тип | Описание |
|---|---|---|
| name | string | Название направления (Токио, Париж, Бали) |
| description | string | Краткое описание |
| imageUrl | string | Путь к изображению (/images/...) |

### TravelOffer
Туристическое предложение, отображаемое на странице /offers.

| Поле | Тип | Описание |
|---|---|---|
| title | string | Название тура |
| country | string | Страна назначения |
| duration | string | Продолжительность (дней) |
| description | string | Описание тура |

---

## Бизнес-правила

| № | Правило |
|---|---|
| BR-1 | Доступ к /offers разрешён только при наличии валидных credentials в localStorage |
| BR-2 | Купон должен содержать ключевое слово и номер в формате XX-XXXXX |
| BR-3 | При переходе на новую страницу CSS предыдущей страницы удаляется |
| BR-4 | Каждая страница обязана возвращать функцию cleanup из mount() |
| BR-5 | Навигация осуществляется только через navigate() — не через href |
| BR-6 | Router не может отрендерить незарегистрированный маршрут |
