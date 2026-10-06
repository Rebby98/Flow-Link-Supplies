// WAIT FOR PAGE TO LOAD
document.addEventListener("DOMContentLoaded", function () {

    // MOBILE MENU
    const menuToggle = document.getElementById("menu-toggle");
    const navLinks = document.getElementById("nav-links");

    if(menuToggle){
        menuToggle.addEventListener("click", () => {
            navLinks.classList.toggle("active");
        });
    }

    // CATEGORY FILTERING
    const categoryButtons = document.querySelectorAll(".category-btn");
    const productCards = document.querySelectorAll(".product-card");

    categoryButtons.forEach(button => {

        button.addEventListener("click", function(e){

            e.preventDefault();

            // ACTIVE BUTTON
            categoryButtons.forEach(btn => {
                btn.classList.remove("active-category");
            });

            button.classList.add("active-category");

            // FILTER VALUE
            const filter = button.getAttribute("data-filter");

            // FILTER PRODUCTS
            productCards.forEach(card => {

                const category =
                    card.getAttribute("data-category");

                if(filter === "all" || category === filter){

                    card.style.display = "";

                } else {

                    card.style.display = "none";

                }

            });

        });

    });

});

// PRODUCT SEARCH

const searchInput = document.getElementById("product-search");

if (searchInput) {

    searchInput.addEventListener("input", function () {

        const searchValue = this.value.toLowerCase().trim();

        productCards.forEach(card => {

            const productName =
                (card.dataset.name || "").toLowerCase();

            if (productName.includes(searchValue)) {

                card.style.display = "block";

            } else {

                card.style.display = "none";

            }

        });

    });

}