(function () {
  'use strict';

  const sidebar = document.querySelector('.sidebar');
  const mainContent = document.querySelector('.main-content');
  let overlay = document.querySelector('.sidebar-overlay');
  const toggleBtn = document.getElementById('sidebarToggle');
  const COLLAPSE_KEY = 'misala.sidebar.collapsed';

  if (!overlay) {
    overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    document.body.appendChild(overlay);
  }

  function readCollapsed() {
    try { return localStorage.getItem(COLLAPSE_KEY) === '1'; }
    catch (e) { return false; }
  }
  function saveCollapsed(v) {
    try { localStorage.setItem(COLLAPSE_KEY, v ? '1' : '0'); }
    catch (e) {}
  }

  (function initCollapsed() {
    const collapsed = readCollapsed();
    if (collapsed && sidebar) sidebar.classList.add('collapsed');
  })();

  function openSidebarMobile() {
    sidebar.classList.add('open');
    overlay.classList.add('show');
    document.documentElement.style.overflow = 'hidden';
  }

  function closeSidebarMobile() {
    sidebar.classList.remove('open');
    overlay.classList.remove('show');
    document.documentElement.style.overflow = '';
    if (toggleBtn) toggleBtn.focus();
  }

  function toggleSidebarDesktop() {
    const collapsed = sidebar.classList.toggle('collapsed');
    saveCollapsed(collapsed);
  }

  if (toggleBtn) {
    toggleBtn.addEventListener('click', (e) => {
      e.preventDefault();
      if (window.matchMedia('(max-width: 992px)').matches) {
        if (sidebar.classList.contains('open')) closeSidebarMobile();
        else openSidebarMobile();
      } else {
        toggleSidebarDesktop();
      }
    });
  }

  overlay.addEventListener('click', closeSidebarMobile);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && sidebar.classList.contains('open')) closeSidebarMobile();
  });
  document.addEventListener('click', (e) => {
    if (window.matchMedia('(max-width: 992px)').matches && sidebar.classList.contains('open')) {
      if (!sidebar.contains(e.target) && (!toggleBtn || !toggleBtn.contains(e.target))) {
        closeSidebarMobile();
      }
    }
  });

  let lastWidth = window.innerWidth;
  window.addEventListener('resize', () => {
    const w = window.innerWidth;
    if (lastWidth <= 992 && w > 992) {
      sidebar.classList.remove('open');
      overlay.classList.remove('show');
      document.documentElement.style.overflow = '';
    }
    lastWidth = w;
  });

  window.misalaSidebar = {
    openMobile: openSidebarMobile,
    closeMobile: closeSidebarMobile,
    toggleDesktop: toggleSidebarDesktop,
    isCollapsed: () => sidebar.classList.contains('collapsed'),
  };
})();
(function () {
  'use strict';

  const sidebar = document.querySelector('.sidebar');
  const mainContent = document.querySelector('.main-content');
  const toggleBtn = document.getElementById('sidebarToggle');
  const COLLAPSE_KEY = 'misala.sidebar.collapsed';
  let overlay = document.querySelector('.sidebar-overlay');

  // Create overlay if not in DOM
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    document.body.appendChild(overlay);
  }

  // ===== Helpers for state persistence =====
  const readCollapsed = () => {
    try { return localStorage.getItem(COLLAPSE_KEY) === '1'; }
    catch { return false; }
  };

  const saveCollapsed = (state) => {
    try { localStorage.setItem(COLLAPSE_KEY, state ? '1' : '0'); }
    catch {}
  };

  // ===== Initialize collapsed state =====
  if (readCollapsed() && sidebar) {
    sidebar.classList.add('collapsed');
  }

  // ===== Sidebar actions =====
  const openSidebarMobile = () => {
    sidebar.classList.add('open');
    overlay.classList.add('show');
    document.documentElement.style.overflow = 'hidden';
  };

  const closeSidebarMobile = () => {
    sidebar.classList.remove('open');
    overlay.classList.remove('show');
    document.documentElement.style.overflow = '';
    if (toggleBtn) toggleBtn.focus(); // accessibility
  };

  const toggleSidebarDesktop = () => {
    const collapsed = sidebar.classList.toggle('collapsed');
    saveCollapsed(collapsed);
  };

  // ===== Event handlers =====
  if (toggleBtn) {
    toggleBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const isMobile = window.matchMedia('(max-width: 992px)').matches;
      if (isMobile) {
        sidebar.classList.contains('open') ? closeSidebarMobile() : openSidebarMobile();
      } else {
        toggleSidebarDesktop();
      }
    });
  }

  overlay.addEventListener('click', closeSidebarMobile);

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && sidebar.classList.contains('open')) {
      closeSidebarMobile();
    }
  });

  document.addEventListener('click', (e) => {
    if (window.matchMedia('(max-width: 992px)').matches && sidebar.classList.contains('open')) {
      if (!sidebar.contains(e.target) && (!toggleBtn || !toggleBtn.contains(e.target))) {
        closeSidebarMobile();
      }
    }
  });

  // ===== Reset overlay when resizing =====
  let lastWidth = window.innerWidth;
  window.addEventListener('resize', () => {
    const w = window.innerWidth;
    if (lastWidth <= 992 && w > 992) {
      sidebar.classList.remove('open');
      overlay.classList.remove('show');
      document.documentElement.style.overflow = '';
    }
    lastWidth = w;
  });

  // ===== Expose minimal API =====
  window.misalaSidebar = {
    openMobile: openSidebarMobile,
    closeMobile: closeSidebarMobile,
    toggleDesktop: toggleSidebarDesktop,
    isCollapsed: () => sidebar.classList.contains('collapsed'),
  };
})();
