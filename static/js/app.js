/**
 * SCSI — app.js
 * Vanilla JS for sidebar toggle, active menu highlights, scroll persistence
 */

(function () {
  'use strict';

  const body = document.body;
  const nav = document.querySelector('.nxl-navigation');

  // ── Sidebar mini-mode toggle ──────────────────────────────────────────────
  const menuMiniBtn = document.getElementById('menu-mini-button');
  const menuExpBtn  = document.getElementById('menu-expend-button');

  if (menuMiniBtn) {
    menuMiniBtn.addEventListener('click', () => {
      body.classList.add('nxl-minimize');
      menuMiniBtn.style.display = 'none';
      if (menuExpBtn) menuExpBtn.style.display = 'inline-flex';
      localStorage.setItem('nxl-minimize', '1');
    });
  }

  if (menuExpBtn) {
    menuExpBtn.addEventListener('click', () => {
      body.classList.remove('nxl-minimize');
      menuExpBtn.style.display = 'none';
      if (menuMiniBtn) menuMiniBtn.style.display = 'inline-flex';
      localStorage.removeItem('nxl-minimize');
    });
  }

  // ── Restore sidebar minimize state ────────────────────────────────────────
  if (localStorage.getItem('nxl-minimize') === '1') {
    body.classList.add('nxl-minimize');
    if (menuMiniBtn) menuMiniBtn.style.display = 'none';
    if (menuExpBtn) menuExpBtn.style.display = 'inline-flex';
  }

  // ── Sidebar scroll position persistence ───────────────────────────────────
  if (nav) {
    const saved = localStorage.getItem('nxl-nav-scroll');
    if (saved) nav.scrollTop = parseInt(saved, 10);

    nav.addEventListener('scroll', () => {
      localStorage.setItem('nxl-nav-scroll', nav.scrollTop);
    });
  }

  // ── Mobile sidebar toggle ─────────────────────────────────────────────────
  const mobileCollapse = document.getElementById('mobile-collapse');
  if (mobileCollapse) {
    mobileCollapse.addEventListener('click', () => {
      body.classList.toggle('nxl-mob-sidebar-active');
    });
  }

  // ── Overlay click closes mobile sidebar ───────────────────────────────────
  const overlay = document.querySelector('.nxl-overlay');
  if (overlay) {
    overlay.addEventListener('click', () => {
      body.classList.remove('nxl-mob-sidebar-active');
    });
  }

  // ── nxl submenu expand ────────────────────────────────────────────────────
  document.querySelectorAll('.nxl-hasmenu > .nxl-link').forEach(link => {
    link.addEventListener('click', function (e) {
      if (!body.classList.contains('nxl-minimize')) {
        e.preventDefault();
        const parent = this.closest('.nxl-hasmenu');
        parent.classList.toggle('active');
        const submenu = parent.querySelector('.nxl-submenu');
        if (submenu) {
          submenu.style.display = parent.classList.contains('active') ? 'block' : 'none';
        }
      }
    });
  });

  // ── Auto-dismiss Django messages ──────────────────────────────────────────
  setTimeout(() => {
    document.querySelectorAll('.alert-dismissible').forEach(el => {
      try {
        if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
          new bootstrap.Alert(el).close();
        } else {
          el.style.display = 'none';
        }
      } catch(e) {
        el.style.display = 'none';
      }
    });
  }, 5000);

  // ── Mark active nav item by current URL ───────────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nxl-navbar .nxl-link[href]').forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '#' && currentPath.startsWith(href)) {
      link.closest('.nxl-item')?.classList.add('active');
      const parent = link.closest('.nxl-hasmenu');
      if (parent) {
        parent.classList.add('active');
        const sub = parent.querySelector('.nxl-submenu');
        if (sub) sub.style.display = 'block';
      }
    }
  });

})();
