/**
 * SCSI — app.js
 * Minimal overrides on top of Duralux theme JS.
 * Sidebar toggle, scroll persistence, active nav, messages auto-dismiss.
 */

(function () {
  'use strict';

  // ── Duralux sidebar toggle uses jQuery + html.minimenu (vendors.min.js).
  //    We only need to handle localStorage persistence for the state.

  $(document).ready(function () {
    // Restore sidebar state from localStorage
    var savedState = localStorage.getItem('nexel-classic-dashboard-menu-mini-theme');
    if (savedState === 'menu-mini-theme') {
      $('html').addClass('minimenu');
      $('#menu-mini-button').hide();
      $('#menu-expend-button').show();
      $('.logo-full').hide();
      $('.logo-abbr').show();
    }

    // Intercept Duralux toggle clicks to save state
    $('#menu-mini-button').on('click', function () {
      localStorage.setItem('nexel-classic-dashboard-menu-mini-theme', 'menu-mini-theme');
    });
    $('#menu-expend-button').on('click', function () {
      localStorage.removeItem('nexel-classic-dashboard-menu-mini-theme');
    });
  });

  // ── Sidebar scroll persistence ──────────────────────────────────────────
  var nav = document.querySelector('.nxl-navigation .navbar-content');
  if (nav) {
    var savedScroll = localStorage.getItem('nxl-nav-scroll');
    if (savedScroll) nav.scrollTop = parseInt(savedScroll, 10);
    nav.addEventListener('scroll', function () {
      localStorage.setItem('nxl-nav-scroll', nav.scrollTop);
    });
  }

  // ── Auto-dismiss Django messages ────────────────────────────────────────
  setTimeout(function () {
    document.querySelectorAll('.alert-dismissible').forEach(function (el) {
      try {
        if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
          new bootstrap.Alert(el).close();
        } else {
          el.style.display = 'none';
        }
      } catch (e) {
        el.style.display = 'none';
      }
    });
  }, 5000);

  // ── Active nav item by URL (backup for Duralux) ────────────────────────
  var currentPath = window.location.pathname;
  document.querySelectorAll('.nxl-navbar .nxl-link[href]').forEach(function (link) {
    var href = link.getAttribute('href');
    if (href && href !== '#' && currentPath.startsWith(href)) {
      var item = link.closest('.nxl-item');
      if (item) item.classList.add('active');
      var parent = link.closest('.nxl-hasmenu');
      if (parent) {
        parent.classList.add('active', 'nxl-trigger');
        var sub = parent.querySelector('.nxl-submenu');
        if (sub) sub.style.display = 'block';
      }
    }
  });

})();
