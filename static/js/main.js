// AJAX-запросы: отзывы, избранное и подсказки поиска

function getCsrfToken() {
    const input = document.querySelector("[name=csrfmiddlewaretoken]");
    return input ? input.value : "";
}

// отправка отзыва без перезагрузки страницы
const reviewForm = document.getElementById("reviewForm");

if (reviewForm) {
    reviewForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const error = document.getElementById("reviewError");
        error.textContent = "";

        fetch(reviewForm.action, {
            method: "POST",
            headers: { "X-CSRFToken": getCsrfToken() },
            body: new FormData(reviewForm),
        })
            .then((response) => response.json())
            .then((data) => {
                if (!data.ok) {
                    error.textContent = data.error;
                    return;
                }

                const empty = document.getElementById("reviewEmpty");
                if (empty) {
                    empty.remove();
                }

                document.getElementById("reviewList").insertAdjacentHTML("afterbegin", data.html);
                document.getElementById("reviewCount").textContent = "(" + data.total + ")";
                reviewForm.reset();
            });
    });
}

// кнопка "в избранное"
const favoriteBtn = document.getElementById("favoriteBtn");

if (favoriteBtn) {
    favoriteBtn.addEventListener("click", function () {
        fetch(favoriteBtn.dataset.url, {
            method: "POST",
            headers: { "X-CSRFToken": getCsrfToken() },
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.in_favorites) {
                    favoriteBtn.textContent = "В избранном";
                    favoriteBtn.className = "btn btn-brand w-100 mb-2";
                } else {
                    favoriteBtn.textContent = "В избранное";
                    favoriteBtn.className = "btn btn-outline-brand w-100 mb-2";
                }
            });
    });
}

// подсказки в поиске
const searchInput = document.getElementById("searchInput");
const suggestBox = document.getElementById("searchSuggest");

if (searchInput && suggestBox) {
    let timer = null;

    searchInput.addEventListener("input", function () {
        clearTimeout(timer);

        const query = searchInput.value.trim();
        if (query.length < 2) {
            suggestBox.hidden = true;
            return;
        }

        // ждём, пока пользователь закончит печатать
        timer = setTimeout(function () {
            fetch(searchInput.dataset.suggestUrl + "?q=" + encodeURIComponent(query))
                .then((response) => response.json())
                .then((data) => {
                    if (data.results.length === 0) {
                        suggestBox.hidden = true;
                        return;
                    }

                    let html = "";
                    for (const tour of data.results) {
                        html +=
                            '<a class="list-group-item list-group-item-action" href="' +
                            tour.url +
                            '">' +
                            tour.title +
                            "<br><small>" +
                            tour.country +
                            " · " +
                            tour.price +
                            " ₽</small></a>";
                    }

                    suggestBox.innerHTML = html;
                    suggestBox.hidden = false;
                });
        }, 300);
    });

    document.addEventListener("click", function (event) {
        if (event.target !== searchInput) {
            suggestBox.hidden = true;
        }
    });
}
