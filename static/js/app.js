/**
 * SCSI — app.js
 * Minimal overrides on top of Duralux theme JS.
 * Sidebar toggle, scroll persistence, active nav, messages auto-dismiss,
 * AI summary AJAX, toast notifications.
 */

(function () {
  'use strict';

  // ── CSRF helper ────────────────────────────────────────────────────────
  function getCSRF() {
    var m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? m[1] : '';
  }

  // ── Toast Notification System ───────────────────────────────────────────
  function showToast(message, type, url) {
    var container = document.getElementById('scsi-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'scsi-toast-container';
      container.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:9999;display:flex;flex-direction:column;gap:8px;pointer-events:none;';
      document.body.appendChild(container);
    }

    var colors = {
      success: { bg: '#17c666', icon: 'feather-check-circle' },
      info:    { bg: '#3454d1', icon: 'feather-info' },
      warning: { bg: '#f0b429', icon: 'feather-alert-circle' },
      error:   { bg: '#ea4d4d', icon: 'feather-x-circle' },
    };
    var c = colors[type] || colors.info;

    var toast = document.createElement('div');
    toast.style.cssText = 'pointer-events:auto;display:flex;align-items:flex-start;gap:10px;padding:14px 18px;background:' + c.bg + ';color:#fff;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.18);font-family:Inter,sans-serif;font-size:14px;max-width:380px;cursor:' + (url ? 'pointer' : 'default') + ';transform:translateX(120%);transition:transform 0.3s ease;';

    toast.innerHTML = '<i class="' + c.icon + '" style="flex-shrink:0;margin-top:1px;"></i><div style="flex:1;min-width:0;"><div style="font-weight:600;margin-bottom:2px;">' + (type === 'success' ? 'Sucesso' : type === 'error' ? 'Erro' : type === 'warning' ? 'Atenção' : 'Notificação') + '</div><div style="opacity:0.9;line-height:1.4;">' + message + '</div></div>';

    if (url) {
      toast.addEventListener('click', function () {
        window.location.href = url;
      });
    }

    container.appendChild(toast);
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        toast.style.transform = 'translateX(0)';
      });
    });

    setTimeout(function () {
      toast.style.transform = 'translateX(120%)';
      setTimeout(function () { toast.remove(); }, 350);
    }, 5000);
  }

  window.scsiToast = showToast;

  // ── AI Summary AJAX ────────────────────────────────────────────────────
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('#btn-ai-summary');
    if (!btn) return;
    e.preventDefault();

    var entityType = btn.dataset.entityType;
    var entityId = btn.dataset.entityId;
    if (!entityType || !entityId) return;

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status"></span>Gerando resumo...';

    fetch('/ia/summarize/' + entityType + '/' + entityId + '/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCSRF() },
    })
    .then(function (r) {
      if (r.status === 503) {
        return r.json().then(function (d) {
          showToast(d.error || 'Serviço de fila indisponível. Contate o administrador.', 'error');
          btn.disabled = false;
          btn.innerHTML = '<i class="feather-cpu me-1"></i>Resumir com IA';
        });
      }
      return r.json();
    })
    .then(function (d) {
      if (!d) return;
      if (d.ok) {
        showToast(d.message, 'success');
        btn.innerHTML = '<i class="feather-cpu me-1"></i>Gerando resumo...';
        btn.classList.remove('btn-outline-primary');
        btn.classList.add('btn-outline-secondary');
      } else {
        showToast(d.error || 'Erro ao gerar resumo', d.error && d.error.indexOf('processando') !== -1 ? 'warning' : 'error');
        btn.disabled = false;
        btn.innerHTML = '<i class="feather-cpu me-1"></i>Resumir com IA';
      }
    })
    .catch(function () {
      showToast('Erro de conexão. Tente novamente.', 'error');
      btn.disabled = false;
      btn.innerHTML = '<i class="feather-cpu me-1"></i>Resumir com IA';
    });
  });

  // ── Duralux sidebar toggle ─────────────────────────────────────────────

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

    // Intercept Duralux toggle clicks to toggle class and persist state
  $('#menu-mini-button').on('click', function () {
    $('html').addClass('minimenu');
    $('#menu-mini-button').hide();
    $('#menu-expend-button').show();
    $('.logo-full').hide();
    $('.logo-abbr').show();
    localStorage.setItem('nexel-classic-dashboard-menu-mini-theme', 'menu-mini-theme');
    $(window).trigger('resize');
  });
  $('#menu-expend-button').on('click', function () {
    $('html').removeClass('minimenu');
    $('#menu-expend-button').hide();
    $('#menu-mini-button').show();
    $('.logo-full').show();
    $('.logo-abbr').hide();
    localStorage.removeItem('nexel-classic-dashboard-menu-mini-theme');
    $(window).trigger('resize');
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

  // ── Notification toast bridge ───────────────────────────────────────────
  // The topbar _topbar.html already polls /notifications/unread/ every 30s.
  // It dispatches a custom event when new notifications arrive; we listen for it
  // to show a toast. This avoids duplicate network requests.
  document.addEventListener('scsi:new-notification', function (e) {
    var n = e.detail;
    if (n) {
      showToast(n.title + ': ' + n.message, 'info', n.url);
    }
  });

})();
