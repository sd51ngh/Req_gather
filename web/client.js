/* Client-facing screen. It only ever receives the server's sanitised snapshot:
 * topic names, a covered/not-covered flag, and the optional "now discussing" spotlight.
 * There is no notes, guidance, scope or priority data in anything this page can fetch. */
(() => {
    'use strict';

    const $ = (id) => document.getElementById(id);
    const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g,
        (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

    const RING_BIG = 326.7;  // 2 * PI * 52
    const RING_SMALL = 113.1; // 2 * PI * 18

    let es = null;
    let retryTimer = null;
    let firstRender = true;
    const expanded = new Set();
    const userToggled = new Set();
    const doneBefore = new Set();
    let lastSpotModule = null;

    function setLive(on) {
        $('live').className = 'live' + (on ? ' on' : '');
        $('live-text').textContent = on ? 'Live' : 'Reconnecting…';
    }

    function show(which) {
        $('gate').hidden = which !== 'gate';
        $('paused').hidden = which !== 'paused';
        $('view').hidden = which !== 'view';
    }

    // --------------------------------------------------------------- rendering
    function render(state) {
        if (!state || state.hidden) { show('paused'); return; }
        show('view');

        const { done, total } = state.progress;
        const pct = total ? Math.round((done / total) * 100) : 0;
        $('big-pct').textContent = pct + '%';
        $('big-count').textContent = `${done} of ${total} covered`;
        $('big-ring-fg').style.strokeDashoffset = String(RING_BIG * (1 - pct / 100));

        const sp = state.spotlight;
        const now = $('now');
        if (sp) {
            now.hidden = false;
            $('now-title').textContent = sp.item_name || sp.module_title;
            $('now-sub').textContent = sp.item_name ? sp.module_title : 'Topic overview';
            if (sp.module_id !== lastSpotModule && !userToggled.has(sp.module_id)) expanded.add(sp.module_id);
        } else {
            now.hidden = true;
        }
        lastSpotModule = sp ? sp.module_id : null;

        renderModules(state, sp);
        firstRender = false;
    }

    function renderModules(state, sp) {
        const wrap = $('modules');
        const existing = new Map(Array.from(wrap.children).map((c) => [c.dataset.id, c]));
        let prev = null;

        state.modules.forEach((m, idx) => {
            let card = existing.get(m.id);
            if (!card) {
                card = document.createElement('article');
                card.className = 'mod';
                card.dataset.id = m.id;
                card.style.animationDelay = firstRender ? (idx * 45) + 'ms' : '0ms';
                card.innerHTML = `
                    <button class="mod-head" type="button" aria-expanded="false">
                        <span class="mod-icon"></span>
                        <span class="mod-text"><h3></h3><p></p></span>
                        <span class="ring"><svg viewBox="0 0 44 44"><circle class="ring-bg" cx="22" cy="22" r="18"></circle><circle class="ring-fg" cx="22" cy="22" r="18"></circle></svg><b></b></span>
                        <span class="chev"></span>
                    </button>
                    <div class="mod-body"><ul></ul></div>`;
                card.querySelector('.mod-head').addEventListener('click', () => {
                    const id = card.dataset.id;
                    userToggled.add(id);
                    if (expanded.has(id)) expanded.delete(id); else expanded.add(id);
                    applyOpen(card);
                });
            }
            existing.delete(m.id);

            const iconEl = card.querySelector('.mod-icon');
            if (iconEl.dataset.src !== m.icon) { iconEl.innerHTML = m.icon; iconEl.dataset.src = m.icon; }
            card.querySelector('h3').textContent = m.title;
            card.querySelector('p').textContent = m.description || '';
            card.querySelector('.ring b').textContent = m.total ? `${m.done}/${m.total}` : '–';
            const frac = m.total ? m.done / m.total : 0;
            card.querySelector('.ring-fg').style.strokeDashoffset = String(RING_SMALL * (1 - frac));
            card.classList.toggle('complete', m.total > 0 && m.done === m.total);
            card.classList.toggle('spot', !!(sp && sp.module_id === m.id));

            const ul = card.querySelector('ul');
            ul.innerHTML = m.items.map((it) => {
                const cls = [];
                if (it.done) cls.push('done');
                if (it.done && !doneBefore.has(it.id) && !firstRender) cls.push('just-done');
                if (sp && sp.item_id === it.id) cls.push('now');
                return `<li class="${cls.join(' ')}"><i></i><span>${esc(it.name)}</span></li>`;
            }).join('');
            m.items.forEach((it) => { if (it.done) doneBefore.add(it.id); else doneBefore.delete(it.id); });

            applyOpen(card);
            if (card.parentNode !== wrap || (prev ? prev.nextSibling !== card : wrap.firstChild !== card)) {
                wrap.insertBefore(card, prev ? prev.nextSibling : wrap.firstChild);
            }
            prev = card;
        });

        existing.forEach((card) => card.remove());

        // Bring the spotlighted topic into view for the room.
        if (sp) {
            const target = wrap.querySelector(`.mod[data-id="${CSS.escape(sp.module_id)}"]`);
            if (target && !firstRender) target.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    function applyOpen(card) {
        const open = expanded.has(card.dataset.id);
        card.classList.toggle('open', open);
        card.querySelector('.mod-head').setAttribute('aria-expanded', String(open));
    }

    // ---------------------------------------------------------------- transport
    function connect() {
        if (es) es.close();
        clearTimeout(retryTimer);
        es = new EventSource('/api/client/events');
        es.onopen = () => setLive(true);
        es.onmessage = (e) => {
            try {
                const msg = JSON.parse(e.data);
                if (msg.type === 'state') render(msg.state);
                else if (msg.type === 'reload') fetchState();
            } catch (err) { console.error(err); }
        };
        es.onerror = () => {
            setLive(false);
            if (es.readyState === 2) { // closed by the browser (e.g. 401) - re-check access, then retry
                retryTimer = setTimeout(boot, 3000);
            }
        };
    }

    async function fetchState() {
        try {
            const res = await fetch('/api/client/state', { credentials: 'same-origin' });
            if (res.ok) render(await res.json());
        } catch (e) { /* the event stream will recover */ }
    }

    async function boot() {
        try {
            const res = await fetch('/api/client/config', { credentials: 'same-origin' });
            const cfg = await res.json();
            if (cfg.requires_code && !cfg.authed) {
                if (es) es.close();
                show('gate');
                setTimeout(() => $('gate-code').focus(), 100);
                return;
            }
            connect();
        } catch (e) {
            setLive(false);
            retryTimer = setTimeout(boot, 3000);
        }
    }

    $('gate-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const err = $('gate-error');
        err.hidden = true;
        try {
            const res = await fetch('/api/client/login', {
                method: 'POST', credentials: 'same-origin',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: $('gate-code').value }),
            });
            const data = await res.json().catch(() => ({}));
            if (!res.ok) { err.textContent = data.error || 'Something went wrong.'; err.hidden = false; return; }
            $('gate-code').value = '';
            boot();
        } catch (ex) { err.textContent = 'Can\'t reach the server.'; err.hidden = false; }
    });

    boot();
})();
