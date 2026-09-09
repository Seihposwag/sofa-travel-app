// Отправка отзыва без перезагрузки страницы

const reviewForm = document.getElementById("reviewForm");

if (reviewForm) {
    reviewForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const error = document.getElementById("reviewError");
        const token = reviewForm.querySelector("[name=csrfmiddlewaretoken]").value;
        error.textContent = "";

        fetch(reviewForm.action, {
            method: "POST",
            headers: { "X-CSRFToken": token },
            body: new FormData(reviewForm),
        })
            .then((response) => response.json())
            .then((data) => {
                if (!data.ok) {
                    error.textContent = data.error;
                    return;
                }

                // если отзывов не было, убираем надпись "отзывов пока нет"
                const empty = document.getElementById("reviewEmpty");
                if (empty) {
                    empty.remove();
                }

                document.getElementById("reviewList").insertAdjacentHTML("afterbegin", data.html);
                document.getElementById("reviewCount").textContent = "(" + data.total + ")";
                reviewForm.reset();
            })
            .catch(() => {
                error.textContent = "Не удалось отправить отзыв, попробуйте ещё раз.";
            });
    });
}
