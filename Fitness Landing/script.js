/* Спорт-ленд — интерактив и анимации */

document.addEventListener('DOMContentLoaded', () => {

  /* ---------- Header scroll ---------- */
  const header = document.getElementById('header');
  const fab = document.querySelector('.fab');

  const onScroll = () => {
    header.classList.toggle('scrolled', window.scrollY > 30);
    if (fab) fab.classList.toggle('show', window.scrollY > 600);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- Mobile menu ---------- */
  const burger = document.getElementById('burger');
  const nav = document.getElementById('nav');

  burger.addEventListener('click', () => {
    burger.classList.toggle('open');
    nav.classList.toggle('open');
  });
  nav.querySelectorAll('a').forEach(link =>
    link.addEventListener('click', () => {
      burger.classList.remove('open');
      nav.classList.remove('open');
    })
  );
  document.addEventListener('click', e => {
    if (!nav.contains(e.target) && !burger.contains(e.target)) {
      burger.classList.remove('open');
      nav.classList.remove('open');
    }
  });

  /* ---------- Reveal on scroll ---------- */
  let pending = new Set(document.querySelectorAll('.reveal'));
  window.__revealPending = pending;

  const showEl = el => {
    el.classList.add('in');
    pending.delete(el);
  };

  const revealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        showEl(entry.target);
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.14, rootMargin: '0px 0px -40px 0px' });

  window.__revealObserver = revealObserver;
  pending.forEach(el => revealObserver.observe(el));

  // Fallback: надёжная проверка при скролле (на случай «пропусков» IO)
  let revealTick = false;
  const checkReveals = () => {
    revealTick = false;
    if (!pending.size) {
      window.removeEventListener('scroll', queueRevealCheck);
      return;
    }
    const limit = window.innerHeight - 40;
    [...pending].forEach(el => {
      if (el.getBoundingClientRect().top < limit) {
        showEl(el);
        revealObserver.unobserve(el);
      }
    });
  };
  const queueRevealCheck = () => {
    if (!revealTick) {
      revealTick = true;
      requestAnimationFrame(checkReveals);
    }
  };
  window.addEventListener('scroll', queueRevealCheck, { passive: true });
  window.addEventListener('resize', queueRevealCheck, { passive: true });
  checkReveals();

  /* ---------- Animated counters ---------- */
  const easeOut = t => 1 - Math.pow(1 - t, 3);

  const animateCount = el => {
    const target = parseFloat(el.dataset.count);
    const prefix = el.dataset.prefix || '';
    const duration = 1400;
    const start = performance.now();

    const tick = now => {
      const progress = Math.min((now - start) / duration, 1);
      el.textContent = prefix + Math.round(easeOut(progress) * target);
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };

  const countObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCount(entry.target);
        countObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.6 });

  document.querySelectorAll('[data-count]').forEach(el => countObserver.observe(el));

  /* ---------- FAQ accordion ---------- */
  document.querySelectorAll('.acc__item').forEach(item => {
    const btn = item.querySelector('.acc__btn');
    const panel = item.querySelector('.acc__panel');

    btn.addEventListener('click', () => {
      const isOpen = item.classList.contains('open');

      document.querySelectorAll('.acc__item.open').forEach(other => {
        other.classList.remove('open');
        other.querySelector('.acc__panel').style.maxHeight = null;
      });

      if (!isOpen) {
        item.classList.add('open');
        panel.style.maxHeight = panel.scrollHeight + 'px';
      }
    });
  });

  window.addEventListener('resize', () => {
    document.querySelectorAll('.acc__item.open .acc__panel').forEach(panel => {
      panel.style.maxHeight = panel.scrollHeight + 'px';
    });
  });

  /* ---------- Smooth anchor scroll (fallback) ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
      const id = anchor.getAttribute('href');
      if (id.length > 1) {
        const target = document.querySelector(id);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    });
  });
});
