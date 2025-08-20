// static/js/wishlist.js

document.addEventListener("DOMContentLoaded", function () {
    const wishlistButtons = document.querySelectorAll(".wishlist-toggle");

    wishlistButtons.forEach(button => {
        button.addEventListener("click", function (e) {
            e.preventDefault();

            const productId = this.dataset.productId;
            const url = this.dataset.url;

            fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.in_wishlist) {
                    this.classList.add("active");
                } else {
                    this.classList.remove("active");
                }
            })
            .catch(err => console.error("Wishlist error:", err));
        });
    });

    // helper: grab CSRF token from cookies
    function getCSRFToken() {
        const name = "csrftoken";
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                return cookie.substring(name.length + 1);
            }
        }
        return "";
    }
});
