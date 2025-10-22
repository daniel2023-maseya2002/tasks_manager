// verify_otp.js

document.addEventListener("DOMContentLoaded", () => {
  const inputs = document.querySelectorAll(".otp-box");
  const form = document.getElementById("otp-form");

  // Move focus to next input automatically
  inputs.forEach((input, index) => {
    input.addEventListener("input", (e) => {
      e.target.value = e.target.value.replace(/[^0-9]/g, ""); // allow only digits
      if (e.target.value.length === 1 && index < inputs.length - 1) {
        inputs[index + 1].focus();
      }
    });

    input.addEventListener("keydown", (e) => {
      if (e.key === "Backspace" && e.target.value === "" && index > 0) {
        inputs[index - 1].focus();
      }
    });
  });

  // Join all digits into one hidden input before submitting
  form.addEventListener("submit", (e) => {
    const otp = Array.from(inputs).map(i => i.value).join("");
    const hidden = document.createElement("input");
    hidden.type = "hidden";
    hidden.name = "otp";
    hidden.value = otp;
    e.target.appendChild(hidden);
  });
});
