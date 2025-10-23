// static/js/page-title.js
document.addEventListener('DOMContentLoaded', () => {
  const wrap = document.querySelector('.page-title-wrap');
  if (!wrap) return;

  // small delay so it feels smooth after other assets load
  setTimeout(() => wrap.classList.add('title-animate'), 80);

  // expose helper for dynamic updates (if you later use PJAX/HTMX)
  window.updatePageTitle = function (newIconClass, newTitle) {
    // find children
    const icon = wrap.querySelector('.page-title-icon');
    const title = wrap.querySelector('.page-title');
    if (!title) return;

    // remove animation class to restart animation
    wrap.classList.remove('title-animate');

    // update contents
    if (icon && newIconClass) {
      // replace icon classes (keeps 'page-title-icon')
      icon.className = 'page-title-icon ' + newIconClass;
    }
    if (newTitle) {
      title.textContent = newTitle;
    }

    // re-add animated class after a tick
    setTimeout(() => wrap.classList.add('title-animate'), 40);
  };
});
