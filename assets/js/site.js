(function () {
  "use strict";

  // 1. Swap in Amazon Attribution links where one has been added.
  var links = window.AATHTHI_AMAZON_LINKS || {};
  document.querySelectorAll("[data-asin]").forEach(function (a) {
    var url = links[a.getAttribute("data-asin")];
    if (url && /^https:\/\/www\.amazon\.com\//.test(url)) a.href = url;
  });

  // 2. Mobile menu.
  var toggle = document.querySelector(".menu-toggle");
  var menu = document.getElementById("menu");
  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      var open = menu.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // 3. Product gallery.
  var main = document.getElementById("main-img");
  document.querySelectorAll(".thumbs button").forEach(function (btn) {
    btn.addEventListener("click", function () {
      main.src = btn.getAttribute("data-full");
      main.alt = btn.querySelector("img").alt;
      document.querySelectorAll(".thumbs button").forEach(function (b) {
        b.setAttribute("aria-current", b === btn ? "true" : "false");
      });
    });
  });

  // 4. Shop filters (works with #party, #couples, #kitchen in the URL too).
  var chips = document.querySelectorAll(".chip");
  if (chips.length) {
    var cards = document.querySelectorAll(".grid .card");
    var apply = function (cat) {
      chips.forEach(function (c) {
        c.setAttribute("aria-pressed", c.getAttribute("data-filter") === cat ? "true" : "false");
      });
      cards.forEach(function (card) {
        card.hidden = !(cat === "all" || card.getAttribute("data-cat") === cat);
      });
    };
    chips.forEach(function (c) {
      c.addEventListener("click", function () {
        var cat = c.getAttribute("data-filter");
        apply(cat);
        history.replaceState(null, "", cat === "all" ? location.pathname : "#" + cat);
      });
    });
    var start = location.hash.replace("#", "");
    if (document.querySelector('.chip[data-filter="' + start + '"]')) apply(start);
  }

  // 5. Footer year.
  var y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();
})();
