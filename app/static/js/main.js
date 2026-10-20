document.addEventListener("DOMContentLoaded", () => {
  // 1. Mobile Sidebar Toggle
  const sidebar = document.querySelector(".app-sidebar");
  const toggleBtn = document.querySelector(".mobile-toggle");

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener("click", (e) => {
      if (
        window.innerWidth <= 992 &&
        sidebar.classList.contains("open") &&
        !sidebar.contains(e.target) &&
        !toggleBtn.contains(e.target)
      ) {
        sidebar.classList.remove("open");
      }
    });
  }

  // 2. Alert Dismissal
  document.querySelectorAll(".alert-close").forEach((btn) => {
    btn.addEventListener("click", () => {
      const alert = btn.closest(".alert");
      if (alert) {
        alert.style.transition = "opacity 0.2s ease, transform 0.2s ease";
        alert.style.opacity = "0";
        alert.style.transform = "translateY(-6px)";
        setTimeout(() => alert.remove(), 200);
      }
    });
  });

  // 3. Auto-dismiss alerts after 6 seconds
  setTimeout(() => {
    document.querySelectorAll(".alert:not(.alert-danger)").forEach((alert) => {
      alert.style.transition = "opacity 0.3s ease";
      alert.style.opacity = "0";
      setTimeout(() => alert.remove(), 300);
    });
  }, 6000);
});

/**
 * Helper to get the CSRF token from the meta tag
 */
function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute("content") : "";
}

/**
 * Standard secure Fetch wrapper with CSRF token and JSON parsing
 */
async function secureFetch(url, options = {}) {
  const defaults = {
    headers: {
      "X-CSRFToken": getCsrfToken(),
      "Content-Type": "application/json",
      "Accept": "application/json",
    },
  };

  const config = {
    ...options,
    headers: {
      ...defaults.headers,
      ...(options.headers || {}),
    },
  };

  const response = await fetch(url, config);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `HTTP error ${response.status}`);
  }
  return response.json();
}
