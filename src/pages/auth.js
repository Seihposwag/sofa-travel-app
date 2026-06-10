import { Page } from "../shared/utils/page";
import { navigate } from "../shared/helpers/navigate";

export const authPage = Page(
  "/auth",
  "Авторизация | Travel World",
  /*html*/ `
<div id="app-page-content">

    <div class="auth-container">

        <div class="auth-card">

            <h1>Travel World</h1>

            <p class="auth-description">
                Для доступа к специальным предложениям введите
                ключевое слово и номер купона.
            </p>

            <form id="auth-form">

                <label>
                    Ключевое слово
                    <input
                        id="keyword"
                        type="text"
                        placeholder="Например: TRAVEL2026"
                        required
                    />
                </label>

                <label>
                    Номер купона
                    <input
                        id="coupon"
                        type="text"
                        placeholder="Например: TW-45821"
                        required
                    />
                </label>

                <button type="submit">
                    Войти
                </button>

            </form>

            <p id="auth-message"></p>

        </div>

    </div>

</div>
`,
  (doc) => {
    const form = doc.querySelector("#auth-form");
    const message = doc.querySelector("#auth-message");

    if (!form) {
      return;
    }

    const submitHandler = (event) => {
      event.preventDefault();

      const keyword = doc.querySelector("#keyword")?.value?.trim();

      const coupon = doc.querySelector("#coupon")?.value?.trim();

      if (!keyword || !coupon) {
        if (message) {
          message.textContent = "Заполните все поля.";
        }

        return;
      }

      localStorage.setItem(
        "credentials",
        JSON.stringify({
          keyword,
          coupon,
          authorizedAt: Date.now(),
        }),
      );

      navigate("/offers");
    };

    form.addEventListener("submit", submitHandler);

    return () => {
      const form = doc.querySelector("#auth-form");

      if (!form || !submitHandler) {
        return;
      }

      form.removeEventListener("submit", submitHandler);
    };
  },
);
