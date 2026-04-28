// ===== GUTENBERG HIGHLIGHT =====
const highlightBtn = document.getElementById("highlightBtn");
const resultBox = document.getElementById("resultBox");
const zones = document.querySelectorAll(".focus-zone");

if (highlightBtn && resultBox && zones.length > 0) {
  highlightBtn.addEventListener("click", () => {
    zones.forEach((zone) => { zone.classList.toggle("active-highlight"); });
    const importantAreas = Array.from(zones)
      .map((zone) => zone.dataset.zone)
      .filter((item) => item && item.trim() !== "")
      .slice(0, 8);
    resultBox.innerHTML = `
      <strong>Наиболее заметные области страницы:</strong>
      <ul>${importantAreas.map((item) => `<li>${item}</li>`).join("")}</ul>
      <p>Эти элементы находятся в верхней части страницы, рядом с кнопками действия, крупными карточками и заголовками.</p>
    `;
  });
  zones.forEach((zone) => {
    zone.addEventListener("mouseenter", () => { zone.style.transform = "translateY(-3px)"; zone.style.transition = "0.2s ease"; });
    zone.addEventListener("mouseleave", () => { zone.style.transform = "translateY(0)"; });
  });
}

// ===== ТЁМНЫЙ РЕЖИМ =====
(function () {
  var btn = document.getElementById("darkToggle");
  var moon = document.getElementById("gc-icon-moon");
  var sun = document.getElementById("gc-icon-sun");

  if (!btn || !moon || !sun) return;

  var isDark = localStorage.getItem("gc-dark") === "1";

  // Применяем только если тёмный режим включён
  if (isDark) {
    document.body.classList.add("dark-mode");
    moon.style.display = "none";
    sun.style.display = "block";
  }
  // Если светлый — не трогаем display, пусть CSS управляет (sun изначально display:none в HTML)

  btn.addEventListener("click", function () {
    isDark = !isDark;
    document.body.classList.toggle("dark-mode", isDark);
    moon.style.display = isDark ? "none" : "";
    sun.style.display = isDark ? "block" : "none";
    localStorage.setItem("gc-dark", isDark ? "1" : "0");
  });
})();