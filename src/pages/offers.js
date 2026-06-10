import { Page } from "../shared/utils/page";
import { navigate } from "../shared/helpers/navigate";

export const offersPage = Page(
  "/offers",
  "Туры и спецпредложения | Travel World",
  /*html*/ `
<div id="app-page-content">

    <nav>
        <a href="#" id="home-page-link">Главная</a>
        <a href="#" id="auth-page-link">Ввести купон</a>
        <a href="#" id="offers-page-link">Путевки</a>
        <a href="#" id="about-page-link">О нас</a>
    </nav>

    <header id="coupon-area">
        <h1>Лучшие предложения для путешествий</h1>
        <p>
            Выберите направление своей мечты и получите бесплатную консультацию
            от наших специалистов.
        </p>
    </header>

    <main>

        <section class="offers-section">

            <h2>Популярные туры</h2>

            <div class="offers-grid">

                <article class="offer-card">
                    <h3>🏝 Бали</h3>
                    <p>7 ночей в отеле 4★ с завтраками.</p>
                    <p><strong>от 890 €</strong></p>
                </article>

                <article class="offer-card">
                    <h3>🗼 Париж</h3>
                    <p>Романтический тур на 5 дней.</p>
                    <p><strong>от 650 €</strong></p>
                </article>

                <article class="offer-card">
                    <h3>🏯 Токио</h3>
                    <p>Знакомство с современной Японией.</p>
                    <p><strong>от 1290 €</strong></p>
                </article>

                <article class="offer-card">
                    <h3>🌴 Мальдивы</h3>
                    <p>Премиальный отдых на берегу океана.</p>
                    <p><strong>от 1590 €</strong></p>
                </article>

            </div>

        </section>

        <section class="consultation-section">

            <h2>Бесплатная горячая линия</h2>

            <p>
                Не уверены какое направление выбрать?
                Наши специалисты помогут подобрать тур,
                ответят на вопросы и подготовят персональное предложение.
            </p>

            <div class="phone-list">
                <div class="phone-card">
                    <h3>🇳🇱 Нидерланды</h3>
                    <a href="tel:+318001234567">
                        +31 800 123 4567
                    </a>
                </div>

                <div class="phone-card">
                    <h3>🇩🇪 Германия</h3>
                    <a href="tel:+498001234567">
                        +49 800 123 4567
                    </a>
                </div>

                <div class="phone-card">
                    <h3>🇫🇷 Франция</h3>
                    <a href="tel:+338001234567">
                        +33 800 123 4567
                    </a>
                </div>

                <div class="phone-card">
                    <h3>🌍 Международная линия</h3>
                    <a href="tel:+18001234567">
                        +1 800 123 4567
                    </a>
                </div>
            </div>

        </section>

    </main>

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
    const couponArea = doc.querySelector("#coupon-area");

    const couponData = localStorage.getItem("credentials")
      ? JSON.parse(localStorage.getItem("credentials"))
      : null;

    if (couponData) {
      const h2 = doc.createElement("h2");
      h2.textContent = "🔥🔥🔥 Вы активировали купон";

      const p = doc.createElement("p");
      p.textContent = `🆔 Секретная фраза: ${couponData.keyword}, номер купона: ${couponData.coupon}`;

      couponArea.appendChild(h2);
      couponArea.appendChild(p);
    }

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
