import { Page } from "../shared/utils/page";
import { navigate } from "../shared/helpers/navigate";

export const aboutUsPage = Page(
  "/about",
  "О нас | Travel World",
  /*html*/ `
<div id="app-page-content">
    <nav>
        <a href="#" id="home-page-link">Главная</a>
        <a href="#" id="auth-page-link">Ввести купон</a>
        <a href="#" id="offers-page-link">Путевки</a>
        <a href="#" id="about-page-link">О нас</a>
    </nav>

    <header>
        <h1>О компании Travel World</h1>
        <p>Ваш надежный партнер в мире путешествий</p>
    </header>

    <div class="container">

        <section class="about-section">
            <h2>Кто мы</h2>

            <p>
                Travel World — современное туристическое агентство,
                которое помогает путешественникам открывать новые страны,
                культуры и впечатления по всему миру.
            </p>

            <p>
                Мы организуем туристические поездки, семейный отдых,
                экскурсионные туры, деловые путешествия и индивидуальные маршруты.
                Наша команда стремится сделать каждую поездку комфортной,
                безопасной и незабываемой.
            </p>

            <p>
                Благодаря многолетнему опыту и сотрудничеству с проверенными
                партнерами по всему миру мы предлагаем качественный сервис
                и выгодные условия для наших клиентов.
            </p>
        </section>

        <section class="about-section">
            <h2>Наша миссия</h2>

            <p>
                Мы верим, что путешествия делают жизнь ярче. Наша цель —
                помогать людям открывать мир, знакомиться с новыми культурами
                и получать незабываемые эмоции от каждой поездки.
            </p>
        </section>

        <section class="stats">

            <div class="stat-card">
                <h3>10+</h3>
                <p>Лет опыта</p>
            </div>

            <div class="stat-card">
                <h3>5000+</h3>
                <p>Довольных клиентов</p>
            </div>

            <div class="stat-card">
                <h3>80+</h3>
                <p>Направлений по миру</p>
            </div>

            <div class="stat-card">
                <h3>24/7</h3>
                <p>Поддержка клиентов</p>
            </div>

        </section>

    </div>

    <footer>
        <p>&copy; 2026 Travel World. Все права защищены.</p>
    </footer>
</div>
`,
  (doc) => {
    const homeLink = doc.querySelector("#home-page-link");
    const authLink = doc.querySelector("#auth-page-link");
    const offersLink = doc.querySelector("#offers-page-link");
    const aboutLink = doc.querySelector("#about-page-link");

    const onNav = (event, path) => {
      event.preventDefault();
      navigate(path);
    };

    const handlers = new Map();

    if (homeLink) {
      handlers.set(homeLink, (e) => onNav(e, "/home"));
      homeLink.addEventListener("click", handlers.get(homeLink));
    }

    if (authLink) {
      handlers.set(authLink, (e) => onNav(e, "/auth"));
      authLink.addEventListener("click", handlers.get(authLink));
    }

    if (offersLink) {
      handlers.set(offersLink, (e) => onNav(e, "/offers"));
      offersLink.addEventListener("click", handlers.get(offersLink));
    }

    if (aboutLink) {
      handlers.set(aboutLink, (e) => onNav(e, "/about"));
      aboutLink.addEventListener("click", handlers.get(aboutLink));
    }

    // cleanup через замыкание
    return () => {
      handlers.forEach((handler, el) => {
        el.removeEventListener("click", handler);
      });
    };
  },
);
