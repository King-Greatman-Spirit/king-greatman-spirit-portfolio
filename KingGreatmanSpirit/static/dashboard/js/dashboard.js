(function () {
  "use strict";

  /* ---------- Sidebar (mobile) ---------- */
  const hamburger = document.querySelector(".dash-hamburger");
  const sidebar = document.querySelector(".dash-sidebar");
  if (hamburger && sidebar) {
    hamburger.addEventListener("click", () => sidebar.classList.toggle("open"));
    document.querySelectorAll(".dash-nav-link, .dash-sidebar-foot a").forEach((a) => {
      a.addEventListener("click", () => sidebar.classList.remove("open"));
    });
  }

  /* ---------- Auto-dismiss flash messages ---------- */
  document.querySelectorAll(".dash-msg").forEach((el) => {
    el.addEventListener("click", () => el.remove());
    setTimeout(() => {
      el.style.transition = "opacity 0.4s, transform 0.4s";
      el.style.opacity = "0";
      el.style.transform = "translateY(-6px)";
      setTimeout(() => el.remove(), 420);
    }, 5200);
  });

  /* ---------- Show / hide password (eye icon) ---------- */
  document.querySelectorAll('.dash-field input[type="password"]').forEach((input) => {
    const wrap = document.createElement("div");
    wrap.className = "dash-pass-box";
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "dash-password-toggle";
    btn.setAttribute("aria-label", "Show password");
    btn.innerHTML = '<i class="bi bi-eye"></i>';
    btn.addEventListener("click", () => {
      const show = input.type === "password";
      input.type = show ? "text" : "password";
      btn.innerHTML = show ? '<i class="bi bi-eye-slash"></i>' : '<i class="bi bi-eye"></i>';
      btn.setAttribute("aria-label", show ? "Hide password" : "Show password");
      input.focus();
    });
    wrap.appendChild(btn);
  });

  /* ---------- Delete confirmation ---------- */
  document.querySelectorAll("[data-confirm]").forEach((el) => {
    el.addEventListener("submit", (e) => {
      const msg = el.getAttribute("data-confirm");
      if (!window.confirm(msg)) e.preventDefault();
    });
  });

  /* ---------- Image previews ---------- */
  document.querySelectorAll("input[type=file][data-preview]").forEach((input) => {
    input.addEventListener("change", () => {
      const targetId = input.getAttribute("data-preview");
      const preview = document.getElementById(targetId);
      if (!preview || !input.files || !input.files[0]) return;
      const url = URL.createObjectURL(input.files[0]);
      const img = document.createElement("img");
      img.src = url;
      preview.innerHTML = "";
      preview.appendChild(img);
    });
  });
})();
