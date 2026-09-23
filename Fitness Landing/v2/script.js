/* Спорт-ленд v2 — интерактив и форма вебинара */

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
  const pending = new Set(document.querySelectorAll('.reveal'));

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

  pending.forEach(el => revealObserver.observe(el));

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

  /* ---------- Smooth anchor scroll ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
      const id = anchor.getAttribute('href');
      if (id.length > 1) {
        const target = document.querySelector(id);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          burger.classList.remove('open');
          nav.classList.remove('open');
        }
      }
    });
  });

  /* ---------- Webinar form ---------- */
  const ENDPOINT = 'https://formsubmit.co/ajax/mar.petrushina@yandex.ru';

  const form = document.getElementById('webinar-form');
  const successBox = document.getElementById('webinar-success');
  const resetBtn = document.getElementById('webinar-reset');
  const submitBtn = form.querySelector('.signup-form__submit');
  const submitLabel = submitBtn.querySelector('.btn__label');

  const phoneDigits = v => v.replace(/\D/g, '');

  const validators = {
    name: v => {
      const t = v.trim();
      if (!t) return 'Укажите ФИО';
      if (t.length < 2) return 'Слишком короткое имя';
      return '';
    },
    phone: v => {
      const d = phoneDigits(v);
      if (!d) return 'Укажите телефон';
      if (d.length < 11) return 'Введите полный номер';
      return '';
    },
    email: v => {
      const t = v.trim();
      if (!t) return 'Укажите email';
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(t)) return 'Проверьте адрес почты';
      return '';
    }
  };

  const showError = (name, msg) => {
    const input = form.elements[name];
    const err = form.querySelector(`[data-error-for="${name}"]`);
    if (msg) {
      input.classList.add('invalid');
      err.textContent = msg;
      err.classList.add('show');
    } else {
      input.classList.remove('invalid');
      err.textContent = '';
      err.classList.remove('show');
    }
    return !msg;
  };

  Object.keys(validators).forEach(name => {
    const input = form.elements[name];
    input.addEventListener('blur', () => showError(name, validators[name](input.value)));
    input.addEventListener('input', () => {
      if (input.classList.contains('invalid')) {
        showError(name, validators[name](input.value));
      }
    });
  });

  /* ---------- Phone mask ---------- */
  const phoneInput = form.elements.phone;
  phoneInput.addEventListener('input', () => {
    let d = phoneDigits(phoneInput.value);
    if (d.startsWith('8')) d = '7' + d.slice(1);
    if (d && !d.startsWith('7')) d = '7' + d;
    d = d.slice(0, 11);
    let out = '';
    if (d.length > 0) out = '+7';
    if (d.length > 1) out += ' (' + d.slice(1, 4);
    if (d.length >= 4) out += ') ' + d.slice(4, 7);
    if (d.length >= 7) out += '-' + d.slice(7, 9);
    if (d.length >= 9) out += '-' + d.slice(9, 11);
    phoneInput.value = out;
  });

  /* ---------- Submit ---------- */
  form.addEventListener('submit', async e => {
    e.preventDefault();

    let ok = true;
    Object.keys(validators).forEach(name => {
      if (!showError(name, validators[name](form.elements[name].value))) ok = false;
    });
    if (!ok) {
      form.querySelector('.invalid')?.focus();
      return;
    }

    submitBtn.disabled = true;
    submitLabel.textContent = 'Отправляем…';

    const payload = {
      ФИО: form.elements.name.value.trim(),
      Телефон: form.elements.phone.value.trim(),
      Email: form.elements.email.value.trim(),
      Источник: 'Вебинар «5 привычек» — лендинг v2',
      _subject: form.elements._subject.value,
      _template: 'table',
      _honey: form.elements._honey.value
    };

    try {
      const res = await fetch(ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json'
        },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error('HTTP ' + res.status);

      form.hidden = true;
      successBox.hidden = false;
      form.reset();
    } catch (err) {
      showError('email', 'Не удалось отправить. Попробуйте ещё раз или напишите нам.');
    } finally {
      submitBtn.disabled = false;
      submitLabel.textContent = 'Записаться на вебинар';
    }
  });

  resetBtn.addEventListener('click', () => {
    successBox.hidden = true;
    form.hidden = false;
    form.querySelector('#wf-name').focus();
  });
});
