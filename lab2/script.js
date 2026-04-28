const highlightBtn = document.getElementById("highlightBtn");
const resultBox = document.getElementById("resultBox");
const zones = document.querySelectorAll(".focus-zone");

if (highlightBtn && resultBox) {
  highlightBtn.addEventListener("click", () => {
    zones.forEach((zone) => {
      zone.classList.toggle("active-highlight");
    });

    const importantAreas = Array.from(zones)
      .map((zone) => zone.dataset.zone)
      .filter(Boolean)
      .slice(0, 8);

    resultBox.innerHTML = `
      <strong>Наиболее заметные области страницы:</strong>
      <ul>
        ${importantAreas.map((item) => `<li>${item}</li>`).join("")}
      </ul>
      Эти элементы находятся в верхней части страницы, рядом с кнопками действия,
      крупными карточками и заголовками.
    `;
  });
}

zones.forEach((zone) => {
  zone.addEventListener("mouseenter", () => {
    zone.style.transform = "translateY(-3px)";
    zone.style.transition = "0.2s ease";
  });

  zone.addEventListener("mouseleave", () => {
    zone.style.transform = "translateY(0)";
  });
});

const userPanel = document.getElementById("userPanel");
const currentUser = JSON.parse(localStorage.getItem("currentUser"));
const registeredUser = JSON.parse(localStorage.getItem("registeredUser"));

if (userPanel && currentUser) {
  userPanel.innerHTML = `
    <div class="user-box">
      <span>Привет, ${currentUser.name}</span>
      <button class="logout-btn" onclick="logout()">Выйти</button>
    </div>
  `;
}

function logout() {
  localStorage.removeItem("currentUser");
  window.location.href = "index.html";
}

const path = window.location.pathname.split("/").pop();

if (path === "catalog.html" && !currentUser) {
  alert("Сначала войдите в аккаунт");
  window.location.href = "register.html";
}

const registerForm = document.getElementById("registerForm");
const loginForm = document.getElementById("loginForm");
const formMessage = document.getElementById("formMessage");
const downloadJsonBtn = document.getElementById("downloadJsonBtn");

let formStartTime = null;
let totalErrors = 0;
let lastRegisteredData = null;

function clearFieldError(inputId, errorId) {
  const input = document.getElementById(inputId);
  const error = document.getElementById(errorId);
  if (input) input.classList.remove("input-error");
  if (error) error.textContent = "";
}

function setFieldError(inputId, errorId, message) {
  const input = document.getElementById(inputId);
  const error = document.getElementById(errorId);
  if (input) input.classList.add("input-error");
  if (error) error.textContent = message;
}

if (registerForm) {
  const inputs = registerForm.querySelectorAll("input, select");

  inputs.forEach((el) => {
    el.addEventListener("focus", () => {
      if (!formStartTime) {
        formStartTime = Date.now();
      }
    });
  });

  registerForm.addEventListener("submit", function (e) {
    e.preventDefault();

    clearFieldError("name", "nameError");
    clearFieldError("email", "emailError");
    clearFieldError("password", "passwordError");

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const satisfaction = Number(document.getElementById("satisfaction").value);

    let isValid = true;
    let currentErrors = 0;

    if (name.length < 2) {
      setFieldError("name", "nameError", "Имя должно содержать минимум 2 символа.");
      isValid = false;
      currentErrors++;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
      setFieldError("email", "emailError", "Введите корректный email.");
      isValid = false;
      currentErrors++;
    }

    if (password.length < 6) {
      setFieldError("password", "passwordError", "Пароль должен содержать минимум 6 символов.");
      isValid = false;
      currentErrors++;
    }

    totalErrors += currentErrors;

    if (!isValid) {
      formMessage.className = "form-message error";
      formMessage.textContent = `Исправьте ошибки в форме. Количество ошибок: ${currentErrors}.`;
      return;
    }

    const endTime = Date.now();
    const taskTime = formStartTime ? ((endTime - formStartTime) / 1000).toFixed(2) : 0;

    lastRegisteredData = {
      name,
      email,
      password,
      satisfaction,
      taskCompletionTimeSeconds: Number(taskTime),
      errorsCount: totalErrors,
      success: true,
      savedAt: new Date().toLocaleString()
    };

    localStorage.setItem("registeredUser", JSON.stringify(lastRegisteredData));
    localStorage.setItem("currentUser", JSON.stringify(lastRegisteredData));

    formMessage.className = "form-message success";
    formMessage.innerHTML =
      `Регистрация прошла успешно.<br>
       Время заполнения: <b>${taskTime} сек.</b><br>
       Ошибок: <b>${totalErrors}</b><br>
       Оценка удобства: <b>${satisfaction}/5</b><br>
       Сейчас вы будете перенаправлены на главную страницу.`;

    registerForm.reset();
    formStartTime = null;
    totalErrors = 0;

    setTimeout(() => {
      window.location.href = "index.html";
    }, 1200);
  });
}

if (loginForm) {
  loginForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value.trim();

    const savedUser = JSON.parse(localStorage.getItem("registeredUser"));

    if (!savedUser) {
      formMessage.className = "form-message error";
      formMessage.textContent = "Сначала зарегистрируйтесь.";
      return;
    }

    if (email === savedUser.email && password === savedUser.password) {
      localStorage.setItem("currentUser", JSON.stringify(savedUser));

      formMessage.className = "form-message success";
      formMessage.innerHTML = `Вход выполнен успешно.<br>Сейчас вы будете перенаправлены на главную страницу.`;

      setTimeout(() => {
        window.location.href = "index.html";
      }, 1200);
    } else {
      formMessage.className = "form-message error";
      formMessage.textContent = "Неверный email или пароль.";
    }
  });
}

if (downloadJsonBtn) {
  downloadJsonBtn.addEventListener("click", () => {
    const stored = localStorage.getItem("registeredUser");

    if (!stored) {
      formMessage.className = "form-message error";
      formMessage.textContent = "Сначала заполните и отправьте форму.";
      return;
    }

    const blob = new Blob([stored], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = "registered_user.json";
    link.click();

    URL.revokeObjectURL(url);
  });
}