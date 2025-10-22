// Toggle password visibility
document.addEventListener('DOMContentLoaded', () => {
  const pwField = document.querySelector('.pw-field');
  const toggle = document.querySelector('.pw-toggle i');
  const btn = document.querySelector('.pw-toggle');

  btn.addEventListener('click', () => {
    if (pwField.type === 'password') {
      pwField.type = 'text';
      toggle.classList.replace('bi-eye-slash', 'bi-eye');
    } else {
      pwField.type = 'password';
      toggle.classList.replace('bi-eye', 'bi-eye-slash');
    }
  });
});
