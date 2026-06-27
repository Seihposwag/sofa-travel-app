# Архитектурная диаграмма — Travel World SPA
> Проект: Travel World SPA | Вариант 8 — Блог о путешествиях

---

## Диаграмма компонентов

```
╔══════════════════════════════════════════════════════════════════╗
║                    Travel World SPA                             ║
║                    (Браузер / Browser)                          ║
║                                                                 ║
║  ┌──────────────────────────────────────────────────────────┐  ║
║  │                    index.html                             │  ║
║  │              <div id="app"></div>                         │  ║
║  │              <script src="/src/main.js">                  │  ║
║  └──────────────────────────┬───────────────────────────────┘  ║
║                             │ import                            ║
║  ┌──────────────────────────▼───────────────────────────────┐  ║
║  │                     main.js                               │  ║
║  │  router.register('/home', homePage)                       │  ║
║  │  router.register('/about', aboutPage)                     │  ║
║  │  router.register('/offers', offersPage)                   │  ║
║  │  router.register('/auth', authPage)                       │  ║
║  │  router.init()                                            │  ║
║  └───────────┬──────────────────────────────┬───────────────┘  ║
║              │ import                        │ import           ║
║  ┌───────────▼───────────┐    ┌─────────────▼─────────────┐   ║
║  │  shared/utils/router  │    │    pages/                  │   ║
║  │  ──────────────────── │    │  ──────────────────────    │   ║
║  │  Router               │    │  homePage    /home         │   ║
║  │  - routes: Map        │    │  aboutPage   /about        │   ║
║  │  - render(path)       │    │  offersPage  /offers       │   ║
║  │  - init()             │    │  authPage    /auth         │   ║
║  └───────────┬───────────┘    └─────────────┬─────────────┘   ║
║              │ uses                          │ uses             ║
║  ┌───────────▼───────────┐    ┌─────────────▼─────────────┐   ║
║  │  shared/utils/page    │    │  shared/helpers/           │   ║
║  │  ──────────────────── │    │  ──────────────────────    │   ║
║  │  Page factory         │    │  navigate.js               │   ║
║  │  - html               │    │  pageStyles.js (CSS mgr)   │   ║
║  │  - mount()            │    │                            │   ║
║  │  - unmount()          │    └─────────────┬─────────────┘   ║
║  └───────────────────────┘                  │ uses             ║
║                                 ┌───────────▼─────────────┐   ║
║  ┌────────────────────────┐     │  Browser APIs            │   ║
║  │  shared/consts/        │     │  ──────────────────────  │   ║
║  │  events.js             │     │  History API             │   ║
║  │  - ROUTE_CHANGE        │     │  (pushState / popstate)  │   ║
║  └────────────────────────┘     │  LocalStorage            │   ║
║                                 │  DOM API                 │   ║
║                                 └─────────────────────────┘   ║
║                                                                 ║
║  ┌──────────────────────────────────────────────────────────┐  ║
║  │                 public/ (статические ресурсы)            │  ║
║  │  styles/home.css   styles/about.css                      │  ║
║  │  styles/auth.css   styles/offers.css                     │  ║
║  │  images/hero-beach.jpg   images/tokyo.jpg                │  ║
║  │  images/paris.jpg        images/bali.jpg                 │  ║
║  │  icons.svg               favicon.svg                     │  ║
║  └──────────────────────────────────────────────────────────┘  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## Схема жизненного цикла страницы

```
  navigate('/home')
        │
        ▼
  Router.render('/home')
        │
        ├─▶ 1. currentCleanup()      ← вызов unmount предыдущей страницы
        │        │
        │        └─▶ removeEventListeners()
        │            removeStyleLink()
        │
        ├─▶ 2. Поиск в routes Map
        │
        ├─▶ 3. page.mount(document)
        │        │
        │        ├─▶ app.innerHTML = page.html
        │        ├─▶ CSS: <link href="/styles/home.css"> → <head>
        │        ├─▶ document.title = page.title
        │        └─▶ return cleanup function
        │
        └─▶ 4. history.pushState({}, '', '/home')
```

---

## Схема авторизации

```
  Пользователь открывает /offers
        │
        ▼
  Router.render('/offers')
        │
        ▼
  Route Guard:
  localStorage.getItem('credentials') ?
        │
   ДА  │                    НЕТ
        ▼                    ▼
  offersPage.mount()    navigate('/auth')
        │                    │
  Показ предложений     authPage.mount()
                             │
                        Форма купона
                             │
                   Ввод keyword + coupon
                             │
                   localStorage.setItem(...)
                             │
                        navigate('/offers')
```

---

## Таблица соответствия маршрутов

| URL | Страница | CSS | Защита | Файл |
|---|---|---|---|---|
| /home | homePage | home.css | Нет | src/pages/home.js |
| /about | aboutPage | about.css | Нет | src/pages/about.js |
| /offers | offersPage | offers.css | Да (купон) | src/pages/offers.js |
| /auth | authPage | auth.css | Нет | src/pages/auth.js |
