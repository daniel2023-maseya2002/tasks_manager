// forgot_password.js

document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  const emailInput = document.querySelector("#email");
  const sendBtn = document.querySelector(".send-btn");

  // Add subtle hover / click animation on the button
  sendBtn.addEventListener("mousedown", () => {
    sendBtn.style.transform = "scale(0.97)";
  });
  sendBtn.addEventListener("mouseup", () => {
    sendBtn.style.transform = "scale(1)";
  });

  // Simple front-end email validation before submitting
  form.addEventListener("submit", (e) => {
    const email = emailInput.value.trim();
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(email)) {
      e.preventDefault();
      emailInput.classList.add("is-invalid");

      // Create or update feedback message
      let feedback = document.querySelector(".invalid-feedback");
      if (!feedback) {
        feedback = document.createElement("div");
        feedback.className = "invalid-feedback";
        feedback.innerText = "Please enter a valid email address.";
        emailInput.parentNode.appendChild(feedback);
      }
      feedback.style.display = "block";
      return;
    }

    // If valid, show a loading animation
    sendBtn.innerHTML = `<div class="spinner-border spinner-border-sm text-light me-2" role="status"></div> Sending...`;
    sendBtn.disabled = true;
  });

  // Remove error when user starts typing again
  emailInput.addEventListener("input", () => {
    if (emailInput.classList.contains("is-invalid")) {
      emailInput.classList.remove("is-invalid");
      const feedback = document.querySelector(".invalid-feedback");
      if (feedback) feedback.style.display = "none";
    }
  });
});
