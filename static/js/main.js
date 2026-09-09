/*
  Слой динамического обновления контента (AJAX).

  Сохраняет подход первой версии интерфейса: работа напрямую с
  браузерными API без сторонних библиотек. Здесь три сценария —
  отправка отзыва, переключение избранного и подсказки поиска.
  Все запросы уходят к обработчикам Django и получают JSON.
*/

(function () {
  "use strict";

  /** Читает значение cookie по имени. Нужно для передачи csrf-токена. */
  function getCookie(name) {
    var match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return match ? decodeURIComponent(match[2]) : null;
  }

  /** Токен берём из скрытого поля формы, иначе из cookie. */
  function csrfToken(form) {
    if (form) {
      var field = form.querySelector("[name=csrfmiddlewaretoken]");
      if (field) {
        return field.value;
      }
    }
    return getCookie("csrftoken");
  }

  function postJSON(url, body, form) {
    return fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfToken(form),
        "X-Requested-With": "XMLHttpRequest",
      },
      body: body,
    });
  }

  // ------------------------------------------------------- отзыв без перезагрузки

  var reviewForm = document.getElementById("reviewForm");

  if (reviewForm) {
    reviewForm.addEventListener("submit", function (event) {
      event.preventDefault();

      var errorBox = document.getElementById("reviewError");
      var button = reviewForm.querySelector("button[type=submit]");
      errorBox.textContent = "";
      button.disabled = true;

      postJSON(reviewForm.action, new FormData(reviewForm), reviewForm)
        .then(function (response) {
          return response.json().then(function (data) {
            return { ok: response.ok, data: data };
          });
        })
        .then(function (result) {
          if (!result.ok || !result.data.ok) {
            errorBox.textContent = (result.data.errors || ["Не удалось отправить отзыв."]).join(" ");
            return;
          }

          var list = document.getElementById("reviewList");
          var placeholder = document.getElementById("reviewEmpty");
          if (placeholder) {
            placeholder.remove();
          }

          list.insertAdjacentHTML("afterbegin", result.data.html);
          document.getElementById("reviewCount").textContent = "(" + result.data.total + ")";
          reviewForm.reset();
        })
        .catch(function () {
          errorBox.textContent = "Ошибка сети. Повторите попытку.";
        })
        .finally(function () {
          button.disabled = false;
        });
    });
  }

  // ------------------------------------------------------- избранное

  var favoriteBtn = document.getElementById("favoriteBtn");

  if (favoriteBtn) {
    favoriteBtn.addEventListener("click", function () {
      favoriteBtn.disabled = true;

      postJSON(favoriteBtn.dataset.url, null, null)
        .then(function (response) {
          return response.json();
        })
        .then(function (data) {
          if (!data.ok) {
            return;
          }

          if (data.in_favorites) {
            favoriteBtn.textContent = "В избранном";
            favoriteBtn.classList.remove("btn-outline-brand");
            favoriteBtn.classList.add("btn-brand");
          } else {
            favoriteBtn.textContent = "В избранное";
            favoriteBtn.classList.remove("btn-brand");
            favoriteBtn.classList.add("btn-outline-brand");
          }
        })
        .finally(function () {
          favoriteBtn.disabled = false;
        });
    });
  }

  // ------------------------------------------------------- подсказки поиска

  var searchInput = document.getElementById("searchInput");
  var suggestBox = document.getElementById("searchSuggest");

  if (searchInput && suggestBox) {
    var timer = null;

    function hideSuggest() {
      suggestBox.hidden = true;
      suggestBox.innerHTML = "";
    }

    function renderSuggest(results) {
      if (!results.length) {
        hideSuggest();
        return;
      }

      suggestBox.innerHTML = results
        .map(function (item) {
          return (
            '<a class="list-group-item list-group-item-action" href="' +
            item.url +
            '">' +
            item.title +
            '<br><small>' +
            item.country +
            " · " +
            item.price +
            " ₽</small></a>"
          );
        })
        .join("");
      suggestBox.hidden = false;
    }

    searchInput.addEventListener("input", function () {
      var query = searchInput.value.trim();
      window.clearTimeout(timer);

      if (query.length < 2) {
        hideSuggest();
        return;
      }

      timer = window.setTimeout(function () {
        var url = searchInput.dataset.suggestUrl + "?q=" + encodeURIComponent(query);

        fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
          .then(function (response) {
            return response.json();
          })
          .then(function (data) {
            renderSuggest(data.results || []);
          })
          .catch(hideSuggest);
      }, 250);
    });

    document.addEventListener("click", function (event) {
      if (!suggestBox.contains(event.target) && event.target !== searchInput) {
        hideSuggest();
      }
    });
  }
})();
