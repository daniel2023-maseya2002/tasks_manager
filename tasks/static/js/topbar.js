(function () {
  "use strict";

  // Language selector
  document.addEventListener("click", (e) => {
    if (e.target.tagName === "BUTTON" && e.target.name === "language") {
      e.preventDefault();
      e.target.closest("form").submit();
    }
  });

  // CSRF helper
  function getCookie(name) {
    const cookies = document.cookie.split(";").map((c) => c.trim());
    for (const c of cookies) {
      if (c.startsWith(name + "=")) return decodeURIComponent(c.split("=")[1]);
    }
    return null;
  }

  // Mark all notifications as read when clicking bell
  document.addEventListener("click", async (e) => {
    const bell = e.target.closest("a[data-mark-url]");
    if (!bell) return;
    const markUrl = bell.dataset.markUrl;
    try {
      await fetch(markUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "X-Requested-With": "XMLHttpRequest",
        },
      });
      const badge = bell.querySelector(".notif-badge");
      if (badge) badge.remove();
    } catch (_) {}
  });

  // Auto-refresh unread count
  const bell = document.querySelector("a[data-unread-url]");
  if (bell) {
    const url = bell.dataset.unreadUrl;
    const interval = parseInt(bell.dataset.unreadInterval || "20000", 10);

    async function updateUnread() {
      try {
        const res = await fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } });
        if (!res.ok) return;
        const data = await res.json();
        const unread = data.unread || 0;
        let badge = bell.querySelector(".notif-badge");
        if (unread > 0) {
          if (!badge) {
            badge = document.createElement("span");
            badge.className = "notif-badge";
            bell.appendChild(badge);
          }
          badge.textContent = unread > 99 ? "99+" : unread;
        } else if (badge) badge.remove();
      } catch (_) {}
    }

    updateUnread();
    setInterval(updateUnread, interval);
  }
})();
