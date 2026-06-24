/**
 * SCSI — app.js
 * Vanilla JS for sidebar toggle, active menu highlights, alerts auto-dismiss
 */

(function () {
  'use strict';

  // ── Sidebar mini-mode toggle ──────────────────────────────────────────────
  const menuMiniBtn = document.getElementById('menu-mini-button');
  const menuExpBtn  = document.getElementById('menu-expend-button');
  const body        = document.body;

  if (menuMiniBtn) {
    menuMiniBtn.addEventListener('click', () => {
      body.classList.add('nxl-minimize');
      if (menuExpBtn) {
        menuMiniBtn.style.display = 'none';
        menuExpBtn.style.display  = 'inline-flex';
      }
    });
  }

  if (menuExpBtn) {
    menuExpBtn.addEventListener('click', () => {
      body.classList.remove('nxl-minimize');
      menuExpBtn.style.display  = 'none';
      if (menuMiniBtn) menuMiniBtn.style.display = 'inline-flex';
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
          if (parent.classList.contains('active')) {
            submenu.style.display = 'block';
          } else {
            submenu.style.display = 'none';
          }
        }
      }
    });
  });

  // ── Auto-dismiss Django messages ──────────────────────────────────────────
  setTimeout(() => {
    document.querySelectorAll('.alert-dismissible').forEach(el => {
      const bsAlert = bootstrap && bootstrap.Alert ? new bootstrap.Alert(el) : null;
      if (bsAlert) bsAlert.close();
      else el.style.display = 'none';
    });
  }, 5000);

  // ── Mark active nav item by current URL ───────────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nxl-navbar .nxl-link[href]').forEach(link => {
    if (link.getAttribute('href') !== '#' && currentPath.startsWith(link.getAttribute('href'))) {
      link.closest('.nxl-item').classList.add('active');
      const parent = link.closest('.nxl-hasmenu');
      if (parent) {
        parent.classList.add('active');
        const sub = parent.querySelector('.nxl-submenu');
        if (sub) sub.style.display = 'block';
      }
    }
  });

})();
