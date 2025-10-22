// reset_password.js

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("reset-form");
  const password1 = document.getElementById("password1");
  const password2 = document.getElementById("password2");
  const resetBtn = document.querySelector(".reset-btn");

  // Small press animation
  resetBtn.addEventListener("mousedown", () => resetBtn.style.transform = "scale(0.97)");
  resetBtn.addEventListener("mouseup", () => resetBtn.style.transform = "scale(1)");

  form.addEventListener("submit", (e) => {
    const pass1 = password1.value.trim();
    const pass2 = password2.value.trim();

    if (pass1.length < 6) {
      e.preventDefault();
      alert("Password must be at least 6 characters long.");
      password1.focus();
      return;
    }

    if (pass1 !== pass2) {
      e.preventDefault();
      alert("Passwords do not match. Please retype.");
      password2.focus();
      return;
    }

    resetBtn.innerHTML = `<div class="spinner-border spinner-border-sm text-light me-2" role="status"></div> Resetting...`;
    resetBtn.disabled = true;
  });
});
