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

  // 3. Product gallery (photos + video).
  var main = document.getElementById("main-img");
  var video = document.getElementById("main-video");
  var thumbBtns = document.querySelectorAll(".thumbs button");
  var select = function (btn) {
    thumbBtns.forEach(function (b) { b.setAttribute("aria-current", b === btn ? "true" : "false"); });
    if (btn.hasAttribute("data-video") && video) {
      var source = video.querySelector("source");
      if (!source.src) { source.src = source.getAttribute("data-src"); video.load(); }
      main.hidden = true; video.hidden = false; main.parentNode.classList.add("is-video");
      var p = video.play(); if (p && p.catch) p.catch(function () {});
    } else {
      if (video) { video.pause(); video.hidden = true; main.parentNode.classList.remove("is-video"); }
      main.hidden = false;
      main.src = btn.getAttribute("data-full");
      main.alt = btn.querySelector("img").alt;
    }
  };
  thumbBtns.forEach(function (btn) { btn.addEventListener("click", function () { select(btn); }); });
  var watch = document.getElementById("watch-video");
  if (watch) watch.addEventListener("click", function () {
    var vb = document.querySelector(".thumbs .vthumb"); if (vb) select(vb);
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
