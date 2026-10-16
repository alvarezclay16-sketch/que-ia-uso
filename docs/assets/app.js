// Qué IA Uso — interacción y animaciones. Todo es mejora progresiva: sin JS el sitio funciona igual.
(function () {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();

  // Aparición al hacer scroll, escalonada
  const rev = $$('.cat, .tool, .plan, .news li, .test, .spon');
  rev.forEach((el, i) => { el.classList.add('rev'); el.style.setProperty('--d', (i % 6) * 60 + 'ms'); });
  if ('IntersectionObserver' in window && !reduce) {
    const io = new IntersectionObserver(es => es.forEach(en => {
      if (en.isIntersecting) { en.target.classList.add('vis'); io.unobserve(en.target); }
    }), { rootMargin: '0px 0px -40px 0px' });
    rev.forEach(el => io.observe(el));
  } else rev.forEach(el => el.classList.add('vis'));

  // Contadores
  $$('[data-count]').forEach(el => {
    const fin = +el.dataset.count;
    if (reduce) { el.textContent = fin; return; }
    const t0 = performance.now(), dur = 1100;
    const paso = t => { const k = Math.min(1, (t - t0) / dur); el.textContent = Math.round(fin * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(paso); };
    requestAnimationFrame(paso);
  });

  // Cinta de novedades: se duplica para que el loop no tenga corte
  const cinta = $('.cinta-in');
  if (cinta) {
    cinta.innerHTML += cinta.innerHTML.replace(/<a /g, '<a tabindex="-1" aria-hidden="true" ');
    cinta.parentElement.addEventListener('touchstart', () => cinta.parentElement.classList.toggle('pausa'), { passive: true });
  }

  // ---------- Portada: buscador + atajos + test ----------
  const datos = $('#datos');
  if (datos) {
    const IDX = JSON.parse(datos.textContent);
    const q = $('#q'), sin = $('#sin'), cards = $$('.cat');
    const STOP = ['para', 'una', 'uno', 'unos', 'unas', 'con', 'del', 'las', 'los', 'que', 'hacer', 'crear', 'mis', 'por', 'como', 'quiero', 'necesito', 'algo', 'sobre', 'mejor', 'ia'];
    let hayMatch = false;
    const filtrar = () => {
      const ws = norm(q.value.trim()).split(/\s+/).filter(w => w.length > 2 && !STOP.includes(w));
      const sc = cards.map(c => {
        const d = IDX.find(x => x.id === c.dataset.id);
        const txt = norm([d.t, d.n, ...d.k, ...d.h].join(' '));
        return ws.filter(w => txt.includes(w)).length;
      });
      const max = Math.max(...sc);
      cards.forEach((c, i) => {
        c.hidden = ws.length > 0 && (max === 0 || sc[i] < max);
        c.classList.toggle('sel', ws.length > 0 && max > 0 && sc[i] === max);
        if (!c.hidden) c.classList.add('vis');
      });
      sin.hidden = !(ws.length > 0 && max === 0);
      hayMatch = ws.length > 0 && max > 0;
    };
    q.addEventListener('input', filtrar);
    q.addEventListener('keydown', ev => {
      if (ev.key === 'Enter' && !ev.isComposing && hayMatch) { const f = cards.find(c => !c.hidden); if (f) location.href = f.href; }
    });
    $$('.atajos button').forEach(b => b.addEventListener('click', () => {
      q.value = b.dataset.q; filtrar(); q.focus();
      $('#cats').scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    }));

    // Ejemplos que se escriben solos en el hueco
    const ejemplos = JSON.parse(q.dataset.ejemplos || '[]');
    if (ejemplos.length && !reduce) {
      let i = 0, j = 0, borrando = false;
      const tic = () => {
        if (document.activeElement === q || q.value) { q.placeholder = ''; return setTimeout(tic, 900); }
        const w = ejemplos[i];
        j += borrando ? -1 : 1;
        q.placeholder = w.slice(0, j);
        if (!borrando && j === w.length) { borrando = true; return setTimeout(tic, 1500); }
        if (borrando && j === 0) { borrando = false; i = (i + 1) % ejemplos.length; }
        setTimeout(tic, borrando ? 28 : 65);
      };
      tic();
    }

    // Test de 2 preguntas
    const test = $('#test');
    if (test) {
      const pasos = $$('.paso', test), barra = $('.barra i', test);
      let cat = null;
      const ir = (n, foco) => {
        pasos.forEach((p, k) => p.classList.toggle('on', k === n));
        barra.style.width = (n / (pasos.length - 1)) * 100 + '%';
        if (foco) { const h = $('h2, .gana', pasos[n]); h.setAttribute('tabindex', '-1'); h.focus({ preventScroll: true }); }
      };
      $$('[data-cat]', test).forEach(b => b.addEventListener('click', () => { cat = b.dataset.cat; ir(1, true); }));
      $$('[data-plata]', test).forEach(b => b.addEventListener('click', () => {
        const d = IDX.find(x => x.id === cat);
        const gratis = b.dataset.plata === 'gratis';
        const r = gratis ? (d.g || d.top) : d.top;
        $('.gana', test).textContent = r.n;
        $('.por', test).textContent = (gratis && !d.g ? 'No hay una buena opción gratis para esto; la mejor es de pago. ' : '') + 'Ideal para ' + r.m + '.';
        const a = $('.ficha', test); a.href = d.url; a.textContent = 'Ver las ' + d.h.length + ' opciones para ' + d.t + ' →';
        const s = $('.sitio', test); s.href = r.u; s.textContent = 'Ir a ' + r.n + ' ↗';
        ir(2, true);
      }));
      $('.volver', test).addEventListener('click', () => ir(0, true));
      ir(0);
    }
  }

  // ---------- Página de tarea: filtros ----------
  const lista = $('.tools');
  if (lista && $('.filtros')) {
    const orig = $$('.tool', lista);
    const estado = { gratis: false, orden: 'rank' };
    const precio = t => (t.dataset.precio === '' ? 1e9 : +t.dataset.precio);
    const aplicar = () => {
      orig.forEach(t => { t.hidden = estado.gratis && t.dataset.free !== '1'; });
      const orden = [...orig].sort((a, b) => estado.orden === 'precio'
        ? precio(a) - precio(b) || +a.dataset.rank - +b.dataset.rank
        : +a.dataset.rank - +b.dataset.rank);
      orden.forEach(t => lista.appendChild(t));
      const vis = orig.filter(t => !t.hidden).length;
      $('#cuenta').textContent = vis === 1 ? '1 herramienta' : vis + ' herramientas';
      $('#vacio').hidden = vis > 0;
    };
    $$('.filtros [data-f]').forEach(b => b.addEventListener('click', () => {
      if (b.dataset.f === 'gratis') { estado.gratis = !estado.gratis; b.setAttribute('aria-pressed', estado.gratis); }
      else {
        estado.orden = b.dataset.f;
        $$('.filtros [data-f="rank"], .filtros [data-f="precio"]').forEach(x => x.setAttribute('aria-pressed', x === b));
      }
      aplicar();
    }));
  }

  // ---------- Patrocina: aviso de pago recibido ----------
  const gracias = $('#gracias');
  if (gracias && new URLSearchParams(location.search).has('gracias')) gracias.hidden = false;
})();
