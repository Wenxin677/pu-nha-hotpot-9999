/* ==========================================================================
   Pu Nha Hotpot 9999 — site behaviour
   Vanilla JavaScript only. Everything degrades gracefully: with JavaScript
   switched off the pages still read, navigate (the mobile menu is pure CSS)
   and the FAQ accordion still opens, because it is built on <details>.
   ========================================================================== */
(function () {
  'use strict';

  var $  = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  /* ---------------------------------------------------------------- nav --- */
  function initNav() {
    var toggle = $('#nav-toggle');
    var menu = $('.menu');
    if (!toggle || !menu) { return; }

    function syncLabel() {
      toggle.setAttribute('aria-label', toggle.checked ? 'Close the menu' : 'Open the menu');
    }
    syncLabel();
    toggle.addEventListener('change', syncLabel);

    // close the mobile menu after following a link
    menu.addEventListener('click', function (event) {
      if (event.target.closest('a') && window.matchMedia('(max-width: 880px)').matches) {
        toggle.checked = false;
        syncLabel();
      }
    });

    // never leave the menu hidden behind a resized viewport
    window.addEventListener('resize', function () {
      if (window.innerWidth > 880 && toggle.checked) {
        toggle.checked = false;
        syncLabel();
      }
    });
  }

  /* ----------------------------------------------------------- dropdowns -- */
  function initDropdowns() {
    var drops = $$('.drop');
    if (!drops.length) { return; }

    function closeAll(except) {
      drops.forEach(function (d) { if (d !== except) { d.open = false; } });
    }

    drops.forEach(function (drop) {
      var summary = $('summary', drop);
      var panel = $('.drop__panel', drop);
      var hoverTimer;

      // pointer users on wide screens: open on hover, close on leave
      drop.addEventListener('mouseenter', function () {
        if (!window.matchMedia('(min-width: 881px)').matches) { return; }
        window.clearTimeout(hoverTimer);
        closeAll(drop);
        drop.open = true;
      });
      drop.addEventListener('mouseleave', function () {
        if (!window.matchMedia('(min-width: 881px)').matches) { return; }
        hoverTimer = window.setTimeout(function () { drop.open = false; }, 220);
      });

      // only one open at a time, and Escape closes
      if (summary) {
        summary.addEventListener('click', function () {
          if (drop.open) { closeAll(null); } else { closeAll(drop); }
        });
      }
      drop.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') { drop.open = false; if (summary) { summary.focus(); } }
      });
      if (panel) {
        panel.addEventListener('focusout', function (event) {
          if (!drop.contains(event.relatedTarget)) { drop.open = false; }
        });
      }
    });

    document.addEventListener('click', function (event) {
      if (!event.target.closest('.drop')) { closeAll(null); }
    });
  }

  /* ------------------------------------------------------- reveal on scroll */
  function initReveal() {
    var items = $$('.reveal');
    if (!items.length) { return; }
    if (!('IntersectionObserver' in window)) {
      items.forEach(function (el) { el.classList.add('is-in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-in');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    items.forEach(function (el) { io.observe(el); });
  }

  /* --------------------------------------------------------- back to top -- */
  function initToTop() {
    var button = $('#to-top');
    if (!button) { return; }
    function update() {
      button.classList.toggle('is-visible', window.scrollY > 420);
    }
    update();
    window.addEventListener('scroll', update, { passive: true });
    button.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      var brand = $('.brand');
      if (brand) { brand.focus({ preventScroll: true }); }
    });
  }

  /* -------------------------------------------------- FAQ: one open only -- */
  function initAccordion() {
    var groups = {};
    $$('.faq details').forEach(function (item) {
      var key = item.closest('.faq');
      (groups[key.dataset.faqId || (key.dataset.faqId = 'g' + Object.keys(groups).length)] = groups[key.dataset.faqId] || []).push(item);
      item.addEventListener('toggle', function () {
        if (!item.open) { return; }
        groups[key.dataset.faqId].forEach(function (other) {
          if (other !== item && other.open) { other.open = false; }
        });
      });
    });
  }

  /* ------------------------------------------------------------- helpers -- */
  function todayISO() {
    var now = new Date();
    var month = String(now.getMonth() + 1).padStart(2, '0');
    var day = String(now.getDate()).padStart(2, '0');
    return now.getFullYear() + '-' + month + '-' + day;
  }

  function messageFor(field) {
    var v = (field.value || '').trim();
    var required = field.required === true;
    var label = (field.getAttribute('data-label') ||
      (field.labels && field.labels.length ? field.labels[0].textContent : 'This field')).replace(/\s*\*$/, '').trim();

    if (field.type === 'checkbox') {
      if (field.checked) { return ''; }
      return required ? 'Please tick this box so we can continue.' : '';
    }
    if (!v) {
      // optional fields are allowed to stay empty — never block a submit on them
      return required ? label + ' is required.' : '';
    }
    if (field.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) {
      return 'Please enter a valid email address, for example you@example.com.';
    }
    if (field.type === 'tel' && !/^[0-9+()\s-]{6,20}$/.test(v)) {
      return 'Please enter a phone number we can reach you on, for example +855 12 345 678.';
    }
    if (field.type === 'number') {
      var n = Number(v);
      var min = field.min !== '' ? Number(field.min) : null;
      var max = field.max !== '' ? Number(field.max) : null;
      if (isNaN(n) || (min !== null && n < min) || (max !== null && n > max)) {
        return 'Please enter a number between ' + field.min + ' and ' + field.max + '.';
      }
    }
    if (field.type === 'date' && v < todayISO()) {
      return 'Please choose today or a future date.';
    }
    if (field.type === 'time' && field.dataset.window) {
      var parts = field.dataset.window.split('-');
      if (v < parts[0] || v > parts[1]) {
        return 'We seat guests between ' + parts[0] + ' and ' + parts[1] + '.';
      }
    }
    if (field.tagName === 'TEXTAREA' && v.length < 10) {
      return 'Please write a little more — at least 10 characters.';
    }
    return '';
  }

  function initForm(form, statusId, successTitle) {
    if (!form) { return; }
    var status = document.getElementById(statusId);

    function fieldError(field) {
      var box = document.getElementById(field.id + '-error');
      var problem = messageFor(field);
      if (box) { box.textContent = problem; }
      if (problem) { field.setAttribute('aria-invalid', 'true'); } else { field.removeAttribute('aria-invalid'); }
      return problem;
    }

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var fields = $$('input, select, textarea', form).filter(function (f) { return f.type !== 'submit' && f.type !== 'reset'; });
      var firstBad = null;
      fields.forEach(function (field) {
        var problem = fieldError(field);
        if (problem && !firstBad) { firstBad = field; }
      });

      if (!status) { return; }
      if (firstBad) {
        status.className = 'form__status form__status--error is-visible';
        status.textContent = 'Almost there — please fix the highlighted fields and try again.';
        firstBad.focus();
        return;
      }

      var lines = [];
      $$('input, select, textarea', form).forEach(function (field) {
        if (!field.name || field.type === 'checkbox' || field.value === '') { return; }
        var label = field.labels && field.labels.length
          ? field.labels[0].textContent.replace(/\s*\*$/, '').trim()
          : field.name;
        lines.push(label + ': ' + field.value);
      });

      var summary = successTitle + ' Thank you — here is what you entered: ' + lines.join(' · ') +
        '. This is a demo form, so nothing was sent to a server and nothing left this device.';
      form.reset();                                   // clear fields first: reset() also clears the status
      $$('.error-text', form).forEach(function (el) { el.textContent = ''; });
      status.className = 'form__status form__status--ok is-visible';
      status.textContent = summary;
    });

    // live feedback once a field has been touched
    $$('input, select, textarea', form).forEach(function (field) {
      field.addEventListener('blur', function () { fieldError(field); });
      field.addEventListener('input', function () {
        if (field.getAttribute('aria-invalid') === 'true') { fieldError(field); }
      });
    });

    form.addEventListener('reset', function () {
      $$('.error-text', form).forEach(function (el) { el.textContent = ''; });
      $$('[aria-invalid]', form).forEach(function (el) { el.removeAttribute('aria-invalid'); });
      if (status) { status.className = 'form__status'; status.textContent = ''; }
    });
  }

  /* ------------------------------------------------------------------ boot */
  document.addEventListener('DOMContentLoaded', function () {
    initNav();
    initDropdowns();
    initReveal();
    initToTop();
    initAccordion();

    var dateInput = document.getElementById('date');
    if (dateInput) {
      dateInput.min = todayISO();
      if (!dateInput.value) { dateInput.value = todayISO(); }
      dateInput.dataset.window = '';
    }
    var timeInput = document.getElementById('time');
    if (timeInput) { timeInput.dataset.window = '11:00-22:00'; }

    initForm($('#booking-form'), 'booking-status', 'Your table request looks good.');
    initForm($('#message-form'), 'message-status', 'Your message is ready.');

    var year = document.getElementById('year');
    if (year) { year.textContent = new Date().getFullYear(); }
  });
})();
