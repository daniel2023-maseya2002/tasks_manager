// signup.js

document.addEventListener("DOMContentLoaded", () => {
  const signupBtn = document.querySelector(".signup-btn");
  const form = document.getElementById("signup-form");

  // Small button animation
  signupBtn.addEventListener("mousedown", () => signupBtn.style.transform = "scale(0.97)");
  signupBtn.addEventListener("mouseup", () => signupBtn.style.transform = "scale(1)");

  form.addEventListener("submit", () => {
    signupBtn.innerHTML = `<div class="spinner-border spinner-border-sm text-light me-2" role="status"></div> Creating...`;
    signupBtn.disabled = true;
  });
});
