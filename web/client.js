/* Client-facing screen. It only ever receives the server's sanitised snapshot:
 * topic names, a covered/not-covered flag, the active company name, and the
 * optional "now discussing" spotlight.
 * The active module card is always kept pinned at the very top of the grid
 * so viewers never have to scroll down to see bottom cards. */
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
    const doneBefore = new Set();
    let lastServerActiveModule = null;
    let localPinnedModuleId = null;
    let lastState = null;

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
        lastState = state;
        show('view');

        // Company header badge
        const comp = state.company;
        const compPill = $('company-pill');
        if (comp && comp.name) {
            compPill.hidden = false;
            $('company-name').textContent = comp.name;
            $('company-preset').textContent = comp.preset_name || 'Manufacturing';
            $('hero-eyebrow').textContent = `${comp.name} · Requirements Workshop`;
        } else {
            compPill.hidden = true;
            $('hero-eyebrow').textContent = 'Requirements workshop';
        }

        const { done, total } = state.progress;
        const pct = total ? Math.round((done / total) * 100) : 0;
        $('big-pct').textContent = pct + '%';
        $('big-count').textContent = `${done} of ${total} covered`;
        $('big-ring-fg').style.strokeDashoffset = String(RING_BIG * (1 - pct / 100));

        const sp = state.spotlight;
        const serverActiveId = (sp && sp.module_id) || state.active_module_id || null;

        // If the server's active/spotlighted module changed, follow the server and auto-expand it at the top
        const serverChanged = serverActiveId && serverActiveId !== lastServerActiveModule;
        if (serverChanged) {
            localPinnedModuleId = null;
            expanded.add(serverActiveId);
        }
        lastServerActiveModule = serverActiveId;

        const activeModuleId = localPinnedModuleId || serverActiveId || (state.modules[0] && state.modules[0].id) || null;
        if (activeModuleId && firstRender) {
            expanded.add(activeModuleId);
        }

        const now = $('now');
        if (sp) {
            now.hidden = false;
            $('now-title').textContent = sp.item_name || sp.module_title;
            $('now-sub').textContent = sp.item_name ? sp.module_title : 'Topic overview';
        } else {
            now.hidden = true;
        }

        renderModules(state, sp, activeModuleId, serverChanged);
        firstRender = false;
    }

    function renderModules(state, sp, activeModuleId, shouldScrollTop) {
        const wrap = $('modules');
        const existing = new Map(Array.from(wrap.children).map((c) => [c.dataset.id, c]));
        let prev = null;

        // Always keep the active card at index 0 (very top of the grid) so users never have to scroll down
        const orderedModules = state.modules.slice().sort((a, b) => {
            const aActive = a.id === activeModuleId ? 0 : 1;
            const bActive = b.id === activeModuleId ? 0 : 1;
            return aActive - bActive;
        });

        orderedModules.forEach((m, idx) => {
            let card = existing.get(m.id);
            if (!card) {
                card = document.createElement('article');
                card.className = 'mod';
                card.dataset.id = m.id;
                card.style.animationDelay = firstRender ? (idx * 45) + 'ms' : '0ms';
                card.innerHTML = `
                    <button class="mod-head" type="button" aria-expanded="false">
                        <span class="mod-icon"></span>
                        <span class="mod-text">
                            <div class="mod-title-row"><h3></h3><span class="mod-active-pill">Active Topic · Top</span></div>
                            <p></p>
                        </span>
                        <span class="ring"><svg viewBox="0 0 44 44"><circle class="ring-bg" cx="22" cy="22" r="18"></circle><circle class="ring-fg" cx="22" cy="22" r="18"></circle></svg><b></b></span>
                        <span class="chev"></span>
                    </button>
                    <div class="mod-body"><ul></ul></div>`;
                card.querySelector('.mod-head').addEventListener('click', () => {
                    const id = card.dataset.id;
                    if (expanded.has(id) && localPinnedModuleId === id) {
                        expanded.delete(id);
                        applyOpen(card);
                    } else {
                        // Promote clicked card to the top of the screen and open it
                        localPinnedModuleId = id;
                        expanded.add(id);
                        if (lastState) render(lastState);
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                    }
                });
            }
            existing.delete(m.id);

            const isActiveCard = m.id === activeModuleId;
            const iconEl = card.querySelector('.mod-icon');
            if (iconEl.dataset.src !== m.icon) { iconEl.innerHTML = m.icon; iconEl.dataset.src = m.icon; }
            card.querySelector('h3').textContent = m.title;
            card.querySelector('p').textContent = m.description || '';
            card.querySelector('.ring b').textContent = m.total ? `${m.done}/${m.total}` : '–';
            const frac = m.total ? m.done / m.total : 0;
            card.querySelector('.ring-fg').style.strokeDashoffset = String(RING_SMALL * (1 - frac));
            card.classList.toggle('complete', m.total > 0 && m.done === m.total);
            card.classList.toggle('spot', isActiveCard);

            // Within the active card, place the spotlighted item at the top of the list so it's immediately visible
            const orderedItems = m.items.slice().sort((a, b) => {
                const aNow = (sp && sp.item_id === a.id) ? 0 : 1;
                const bNow = (sp && sp.item_id === b.id) ? 0 : 1;
                return aNow - bNow;
            });

            const ul = card.querySelector('ul');
            ul.innerHTML = orderedItems.map((it) => {
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

        // Keep viewport at the top when the active card updates so the top-pinned card is always visible
        if (shouldScrollTop && !firstRender && window.scrollY > 180) {
            window.scrollTo({ top: 0, behavior: 'smooth' });
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
