import { Page } from "../shared/utils/page";
import { navigate } from "../shared/helpers/navigate";

export const homePage = Page(
  "/home",
  "Главная | Travel World",
  /*html*/ `
<div id="app-page-content">
    <header>
        <nav>
            <div class="logo">🌍 Travel World</div>

            <ul>
                <li><a href="#" id="home-page-link">Главная</a></li>
                <li><a href="#" id="auth-page-link">Ввести купон</a></li>
                <li><a href="#" id="offers-page-link">Путевки</a></li>
                <li><a href="#" id="about-page-link">О нас</a></li>
            </ul>
        </nav>

        <div class="hero">
            <h1>Откройте мир вместе с нами</h1>
            <p>
                Путешествуйте по самым красивым уголкам планеты,
                вдохновляйтесь новыми культурами и создавайте незабываемые воспоминания.
            </p>
            <a href="#" class="btn" id="offers-page-btn">Начать путешествие</a>
        </div>
    </header>

    <section>
        <h2 class="section-title">Популярные направления</h2>
        <div class="destinations">

            <div class="card">
                <img src="/images/tokyo.jpg" alt="Токио">
                <div class="card-content">
                    <h3>Токио</h3>
                    <p>Современные технологии, культура и удивительная кухня Японии.</p>
                </div>
            </div>

            <div class="card">
                <img src="/images/paris.jpg" alt="Париж">
                <div class="card-content">
                    <h3>Париж</h3>
                    <p>Город любви, искусства и легендарной Эйфелевой башни.</p>
                </div>
            </div>

            <div class="card">
                <img src="/images/bali.jpg" alt="Бали">
                <div class="card-content">
                    <h3>Бали</h3>
                    <p>Тропические пляжи, экзотическая природа и отдых мечты.</p>
                </div>
            </div>

        </div>
    </section>

    <footer>
        <p>&copy; 2026 Travel World. Все права защищены.</p>
    </footer>
</div>
`,
  (doc) => {
    const homeLink = doc.querySelector("#home-page-link");
    const authLink = doc.querySelector("#auth-page-link");
    const offersBtn = doc.querySelector("#offers-page-btn");
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

    if (offersBtn) {
      handlers.set(offersBtn, (e) => onNav(e, "/offers"));
      offersBtn.addEventListener("click", handlers.get(offersBtn));
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
