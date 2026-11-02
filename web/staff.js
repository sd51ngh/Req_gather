/* Requirement Gathering - team workspace.
 * The server is the source of truth. Changes are sent as small, targeted requests
 * (one field, or one appended note) and every teammate receives them live via
 * Server-Sent Events, so people never overwrite each other's work. */
(() => {
    'use strict';

    const $ = (id) => document.getElementById(id);
    const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g,
        (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

    const ICONS = {
        pencil: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px"><path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" /></svg>',
        trash: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>',
        x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>',
        monitor: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" /><path stroke-linecap="round" d="M8 21h8M12 17v4" /></svg>',
        edit: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width:11px;height:11px;margin-right:2px"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" /><path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z" /></svg>',
        copy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width:11px;height:11px;margin-right:2px"><rect x="9" y="9" width="13" height="13" rx="2" ry="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" /></svg>',
        send: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.27 3.13a.75.75 0 011-.88l17 8.5a.75.75 0 010 1.34l-17 8.5a.75.75 0 01-1-.88L6 12zm0 0h7.5" /></svg>',
    };

    const SCOPE_LABELS = { in: 'In Scope', nice: 'Nice-to-Have', out: 'Out of Scope', pending: 'Unassigned' };
    const PRIORITY_LABELS = { phase1: 'Phase 1', phase2: 'Phase 2', future: 'Future' };

    // ------------------------------------------------------------------ state
    const S = {
        me: null,
        company: null,
        companies: [],
        presets: [],
        selectedPresetId: 'metal_fabrication',
        modules: [],
        presence: [],
        spotlight: null,
        clientHidden: false,
        loaded: false,
        activeModuleId: null,
        editingModuleId: null,
        suppressedOpen: false,
        drafts: new Map(),      // itemId -> unsent note text (survives live re-renders)
        editing: null,          // { noteId, text } while someone edits one of their notes
        fresh: new Set(),       // note ids to flash
        es: null,
        toastTimer: null,
    };

    // ---------------------------------------------------------------- helpers
    class ApiError extends Error {
        constructor(status, message) { super(message); this.status = status; }
    }

    async function api(method, url, body) {
        const opts = { method, credentials: 'same-origin', headers: {} };
        if (body !== undefined) {
            opts.headers['Content-Type'] = 'application/json';
            opts.body = JSON.stringify(body);
        }
        let res;
        try { res = await fetch(url, opts); }
        catch (e) { throw new ApiError(0, 'Can\'t reach the server. Check your connection.'); }
        let data = null;
        try { data = await res.json(); } catch (e) { /* no body */ }
        if (res.status === 401 && url !== '/api/login') showLogin();
        if (!res.ok) throw new ApiError(res.status, (data && data.error) || res.statusText);
        return data;
    }

    function toast(message) {
        const el = $('toast');
        el.textContent = message;
        el.classList.add('show');
        clearTimeout(S.toastTimer);
        S.toastTimer = setTimeout(() => el.classList.remove('show'), 2200);
    }

    const findModule = (id) => S.modules.find((m) => m.id === id);
    function findItem(id) {
        for (const mod of S.modules) {
            const item = mod.items.find((i) => i.id === id);
            if (item) return { mod, item };
        }
        return null;
    }

    function hue(name) {
        let h = 0;
        for (const ch of String(name)) h = (h * 31 + ch.charCodeAt(0)) % 360;
        return h;
    }
    function initials(name) {
        const parts = String(name).trim().split(/\s+/).filter(Boolean);
        if (!parts.length) return '?';
        return (parts[0][0] + (parts.length > 1 ? parts[parts.length - 1][0] : '')).toUpperCase();
    }
    function avatarHtml(name, cls) {
        return `<div class="${cls}" style="--hue:${hue(name)}" title="${esc(name)}">${esc(initials(name))}</div>`;
    }
    function fullTime(ts) { return new Date(ts * 1000).toLocaleString(); }
    function relTime(ts) {
        const s = Math.max(0, Date.now() / 1000 - ts);
        if (s < 45) return 'just now';
        if (s < 3600) return Math.round(s / 60) + ' min ago';
        if (s < 86400) return Math.round(s / 3600) + ' h ago';
        const d = new Date(ts * 1000);
        return d.toLocaleDateString(undefined, { day: 'numeric', month: 'short' }) + ' ' +
            d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function download(filename, text, type) {
        const blob = new Blob([text], { type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = filename;
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    }

    // ---------------------------------------------------------- auth & session
    function showLogin(message) {
        document.body.classList.remove('logged-in');
        S.loaded = false;
        if (S.es) { S.es.close(); S.es = null; }
        if (S.activeModuleId) closeDrawer(true);
        if (message) { $('login-error').textContent = message; $('login-error').style.display = 'block'; }
        setTimeout(() => $('username').focus(), 100);
    }

    async function enterApp(user) {
        S.me = user;
        document.body.classList.add('logged-in');
        document.body.classList.toggle('is-admin', user.role === 'admin');
        $('login-error').style.display = 'none';
        $('user-chip-name').textContent = user.display_name;
        $('user-chip-role').textContent = user.role === 'admin' ? 'Administrator' : 'Team member';
        $('user-chip-avatar').textContent = initials(user.display_name);
        $('user-chip-avatar').style.setProperty('--hue', hue(user.display_name));
        await loadState();
        connectEvents();
    }

    async function loadState() {
        const d = await api('GET', '/api/state');
        S.me = d.user;
        S.company = d.company || null;
        S.companies = d.companies || [];
        S.presets = d.presets || [];
        S.modules = d.modules;
        S.spotlight = d.spotlight;
        S.clientHidden = d.client_hidden;
        S.presence = d.presence;
        S.loaded = true;
        renderAll();
    }

    function setLive(on) {
        $('live-pill').className = 'live-pill ' + (on ? 'on' : 'off');
        $('live-pill-text').textContent = on ? 'Live' : 'Reconnecting…';
    }

    function connectEvents() {
        if (S.es) S.es.close();
        const es = new EventSource('/api/events');
        S.es = es;
        es.onopen = () => { setLive(true); loadState().catch(() => { }); };
        es.onmessage = (e) => {
            try { applyEvent(JSON.parse(e.data)); } catch (err) { console.error('Bad event', err); }
        };
        es.onerror = () => {
            setLive(false);
            if (es.readyState === 2) { // closed for good (e.g. session expired)
                api('GET', '/api/me').then(() => connectEvents()).catch(() => { });
            }
        };
    }

    // ----------------------------------------------------------- live updates
    function applyEvent(ev) {
        if (ev.type === 'presence') { S.presence = ev.users; renderPresence(); return; }
        if (!S.loaded) return;
        const mine = ev.by_id === S.me.id;

        switch (ev.type) {
            case 'spotlight':
                S.spotlight = ev.spotlight; renderCards(); renderClientControls(); refreshSpotlightButtons(); break;
            case 'client_screen':
                S.clientHidden = ev.hidden; renderClientControls();
                if (!mine) toast(`${ev.by} ${ev.hidden ? 'hid' : 'showed'} the client screen`);
                break;
            case 'reload':
                loadState().catch(() => { });
                if (!mine) toast(`${ev.by} reloaded the data`);
                break;
            case 'company_switched':
                if (S.activeModuleId) closeDrawer(true);
                loadState().catch(() => { });
                if (!mine && ev.company) toast(`${ev.by} switched to "${ev.company.name}"`);
                break;
            case 'company_updated':
                loadState().catch(() => { });
                break;
            case 'module_added':
                if (!findModule(ev.module.id)) S.modules.push(Object.assign({}, ev.module, { items: [] }));
                renderCards(); updateOverallProgress();
                break;
            case 'module_updated': {
                const mod = findModule(ev.module.id);
                if (mod) { mod.title = ev.module.title; mod.description = ev.module.description; }
                renderCards();
                if (S.activeModuleId === ev.module.id) renderDrawerHeader();
                break;
            }
            case 'module_deleted':
                S.modules = S.modules.filter((m) => m.id !== ev.module_id);
                if (S.activeModuleId === ev.module_id) { closeDrawer(true); if (!mine) toast('This module was deleted by ' + ev.by); }
                renderCards(); updateOverallProgress();
                break;
            case 'item_added': {
                const mod = findModule(ev.item.module_id);
                if (mod && !mod.items.some((i) => i.id === ev.item.id)) mod.items.push(Object.assign({ notes: [] }, ev.item));
                afterStructureChange(ev.item.module_id);
                break;
            }
            case 'item_deleted': {
                const mod = findModule(ev.module_id);
                if (mod) mod.items = mod.items.filter((i) => i.id !== ev.item_id);
                S.drafts.delete(ev.item_id);
                afterStructureChange(ev.module_id);
                break;
            }
            case 'item_updated': {
                const found = findItem(ev.item.id);
                if (!found) break;
                const structural = found.item.suppressed !== ev.item.suppressed || found.item.name !== ev.item.name ||
                    found.item.guidance !== ev.item.guidance;
                Object.assign(found.item, ev.item);
                if (structural) afterStructureChange(found.mod.id);
                else { renderCards(); updateOverallProgress(); if (S.activeModuleId === found.mod.id) { refreshItemControls(found.item.id); updateDrawerSummary(); } }
                break;
            }
            case 'note_added': {
                const found = findItem(ev.note.item_id);
                if (!found) break;
                if (!found.item.notes.some((n) => n.id === ev.note.id)) found.item.notes.push(ev.note);
                if (!mine) S.fresh.add(ev.note.id);
                renderNotesFeed(found.item.id, true);
                if (!mine && S.activeModuleId === found.mod.id) toast(`${ev.by} added a note to "${found.item.name}"`);
                break;
            }
            case 'note_updated': {
                const found = findItem(ev.note.item_id);
                if (!found) break;
                const idx = found.item.notes.findIndex((n) => n.id === ev.note.id);
                if (idx >= 0) found.item.notes[idx] = ev.note;
                renderNotesFeed(found.item.id);
                break;
            }
            case 'note_deleted': {
                const found = findItem(ev.item_id);
                if (!found) break;
                found.item.notes = found.item.notes.filter((n) => n.id !== ev.note_id);
                if (S.editing && S.editing.noteId === ev.note_id) S.editing = null;
                renderNotesFeed(found.item.id);
                break;
            }
            default: break;
        }
    }

    function afterStructureChange(moduleId) {
        renderCards(); updateOverallProgress();
        if (S.activeModuleId === moduleId) { renderDrawerList(); updateDrawerSummary(); }
    }

    // ----------------------------------------------------------------- render
    function renderAll() {
        renderCompanyUI(); renderPresence(); renderCards(); updateOverallProgress(); renderClientControls();
        if (S.activeModuleId) {
            if (findModule(S.activeModuleId)) { renderDrawerHeader(); renderDrawerList(); updateDrawerSummary(); }
            else closeDrawer(true);
        }
    }

    function renderCompanyUI() {
        const comp = S.company;
        if (comp) {
            $('header-company-name').textContent = comp.name;
            $('header-company-preset').textContent = comp.preset_name || '';
            $('sidebar-company-preset').textContent = comp.preset_name || '';
        }
        const sel = $('quick-company-select');
        if (sel) {
            sel.innerHTML = S.companies.map((c) =>
                `<option value="${esc(c.id)}"${c.is_active ? ' selected' : ''}>${esc(c.name)}</option>`
            ).join('');
        }
        if ($('companies-modal').classList.contains('open')) {
            renderCompaniesModal();
        }
    }

    function renderPresence() {
        const el = $('presence-stack');
        const shown = S.presence.slice(0, 6);
        el.innerHTML = shown.map((u) => {
            const me = S.me && u.id === S.me.id;
            return `<div class="presence-avatar${me ? ' me' : ''}" style="--hue:${hue(u.name)}" title="${esc(u.name)}${me ? ' (you)' : ''}">${esc(initials(u.name))}</div>`;
        }).join('') + (S.presence.length > 6 ? `<span class="presence-more">+${S.presence.length - 6}</span>` : '') +
            (S.presence.length ? `<span class="presence-more">${S.presence.length} online</span>` : '');
    }

    function renderClientControls() {
        const label = $('client-screen-label');
        const btn = $('btn-client-screen');
        label.textContent = S.clientHidden ? 'Show client screen' : 'Hide client screen';
        btn.classList.toggle('attention', S.clientHidden);
        $('btn-clear-spotlight').disabled = !S.spotlight;
    }

    function activeItemsOf(mod) { return mod.items.filter((i) => !i.suppressed); }

    function updateOverallProgress() {
        let total = 0, scoped = 0;
        S.modules.forEach((m) => activeItemsOf(m).forEach((i) => { total++; if (i.scope !== 'pending') scoped++; }));
        const pct = total ? Math.round((scoped / total) * 100) : 0;
        $('overall-percentage').textContent = pct + '%';
        $('overall-progress-bar').style.width = pct + '%';
        $('completed-stats').textContent = `${scoped} of ${total} items scoped`;
    }

    function renderCards() {
        const grid = $('cards-grid');
        grid.innerHTML = '';
        S.modules.forEach((mod) => {
            const active = activeItemsOf(mod);
            const scoped = active.filter((i) => i.scope !== 'pending').length;
            const pct = active.length ? Math.round((scoped / active.length) * 100) : 0;
            const isSpot = S.spotlight && S.spotlight.module_id === mod.id;
            const card = document.createElement('div');
            card.className = 'mrp-card' + (isSpot ? ' is-spotlight' : '');
            card.dataset.id = mod.id;
            card.innerHTML = `
                ${isSpot ? '<span class="card-spotlight-tag">On client screen</span>' : ''}
                <div class="card-top">
                    <div class="card-icon-wrapper">${mod.icon}</div>
                    <h3>${esc(mod.title)}</h3>
                    <p class="card-desc">${esc(mod.description)}</p>
                </div>
                <div class="card-bottom">
                    <div class="card-progress-bar" title="${pct}% Complete"><div class="card-progress-fill" style="width:${pct}%;"></div></div>
                    <span class="card-badge">${scoped}/${active.length} scoped</span>
                </div>`;
            card.addEventListener('click', () => openDrawer(mod.id));
            grid.appendChild(card);
        });
        const add = document.createElement('div');
        add.className = 'mrp-card add-card-trigger';
        add.innerHTML = `
            <div class="card-add-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width:24px;height:24px"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" /></svg></div>
            <h3>Add Custom Module</h3>
            <p class="card-desc">Create a new business module card to gather customized requirements.</p>`;
        add.addEventListener('click', () => openModuleModal(null));
        grid.appendChild(add);
    }

    // ----------------------------------------------------------------- drawer
    const drawer = () => $('drawer');

    function renderDrawerHeader() {
        const mod = findModule(S.activeModuleId);
        if (!mod) return;
        $('drawer-title').textContent = mod.title;
        $('drawer-subtitle').textContent = `Gathering requirements for: ${mod.title}`;
        $('drawer-module-icon').innerHTML = mod.icon;

        drawer().querySelectorAll('.btn-present-module, .btn-edit-module, .btn-delete-module').forEach((b) => b.remove());
        const closeBtn = $('btn-close-drawer');
        const isSpot = S.spotlight && S.spotlight.module_id === mod.id && !S.spotlight.item_id;

        const present = document.createElement('button');
        present.className = 'btn-present-module' + (isSpot ? ' active' : '');
        present.innerHTML = `${ICONS.monitor}<span>${isSpot ? 'On client screen' : 'Show module to client'}</span>`;
        present.addEventListener('click', () => toggleSpotlight({ module_id: mod.id }));
        closeBtn.parentNode.insertBefore(present, closeBtn);

        if (mod.custom) {
            const edit = document.createElement('button');
            edit.className = 'btn-edit-module';
            edit.innerHTML = `${ICONS.pencil} Edit Module`;
            edit.addEventListener('click', () => openModuleModal(mod.id));
            const del = document.createElement('button');
            del.className = 'btn-delete-module';
            del.innerHTML = `${ICONS.trash.replace('<svg', '<svg style="width:14px;height:14px"')} Delete Module`;
            del.addEventListener('click', () => deleteModule(mod.id));
            closeBtn.parentNode.insertBefore(edit, closeBtn);
            closeBtn.parentNode.insertBefore(del, closeBtn);
        }
    }

    function openDrawer(moduleId) {
        const mod = findModule(moduleId);
        if (!mod) return;
        S.activeModuleId = moduleId;
        renderDrawerHeader();
        renderDrawerList();
        updateDrawerSummary();

        // Automatically spotlight the opened module on the client screen so it stays pinned at the top
        if (!S.spotlight || S.spotlight.module_id !== moduleId) {
            api('PUT', '/api/spotlight', { module_id: moduleId }).catch(() => { });
        }

        const d = drawer();
        const cardEl = document.querySelector(`.mrp-card[data-id="${CSS.escape(moduleId)}"]`);
        if (cardEl) {
            const rect = cardEl.getBoundingClientRect();
            d.style.transition = 'none';
            d.style.top = rect.top + 'px'; d.style.left = rect.left + 'px';
            d.style.width = rect.width + 'px'; d.style.height = rect.height + 'px';
            d.style.borderRadius = '16px';
            d.style.transform = 'perspective(1500px) rotateY(-180deg) rotateZ(12deg) scale(0.9)';
            d.offsetHeight; // force reflow
            d.style.transition = 'all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.1), visibility 0s linear 0s';
            if (window.innerWidth <= 600) {
                d.style.top = '0'; d.style.left = '0'; d.style.width = '100vw'; d.style.height = '100vh'; d.style.borderRadius = '0';
            } else {
                d.style.top = '5vh'; d.style.left = '10vw'; d.style.width = '80vw'; d.style.height = '90vh'; d.style.borderRadius = '24px';
            }
            d.style.transform = 'perspective(1500px) rotateY(0deg) rotateZ(0deg) scale(1)';
        }
        d.classList.add('open');
        $('drawer-overlay').classList.add('open');
    }

    function closeDrawer(immediate) {
        if (!S.activeModuleId) return;
        const d = drawer();
        const cardEl = document.querySelector(`.mrp-card[data-id="${CSS.escape(S.activeModuleId)}"]`);
        if (cardEl && !immediate) {
            const rect = cardEl.getBoundingClientRect();
            d.style.transition = 'all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.1), visibility 0s linear 0.8s';
            d.style.top = rect.top + 'px'; d.style.left = rect.left + 'px';
            d.style.width = rect.width + 'px'; d.style.height = rect.height + 'px';
            d.style.borderRadius = '16px';
            d.style.transform = 'perspective(1500px) rotateY(180deg) rotateZ(-12deg) scale(0.9)';
        }
        d.classList.remove('open');
        $('drawer-overlay').classList.remove('open');
        S.activeModuleId = null;
        S.editing = null;
        setTimeout(() => {
            if (S.activeModuleId === null) {
                ['transition', 'top', 'left', 'width', 'height', 'borderRadius', 'transform'].forEach((p) => { d.style[p] = ''; });
            }
        }, 800);
    }

    function updateDrawerSummary() {
        const mod = findModule(S.activeModuleId);
        if (!mod) return;
        const a = activeItemsOf(mod);
        $('mod-in-scope').textContent = a.filter((i) => i.scope === 'in').length;
        $('mod-nice-have').textContent = a.filter((i) => i.scope === 'nice').length;
        $('mod-out-scope').textContent = a.filter((i) => i.scope === 'out').length;
        $('mod-pending').textContent = a.filter((i) => i.scope === 'pending').length;
    }

    function noteHtml(n) {
        const canChange = S.me && (n.user_id === S.me.id || S.me.role === 'admin');
        const editing = S.editing && S.editing.noteId === n.id;
        const body = editing
            ? `<textarea class="note-edit-textarea" data-note-id="${n.id}">${esc(S.editing.text)}</textarea>
               <div class="note-edit-actions">
                   <button class="btn-secondary" data-action="note-cancel" style="padding:.3rem .75rem;font-size:.72rem">Cancel</button>
                   <button class="btn-primary" data-action="note-save" style="padding:.3rem .75rem;font-size:.72rem">Save</button>
               </div>`
            : `<div class="note-body">${esc(n.body)}</div>`;
        return `<div class="note-entry${S.fresh.has(n.id) ? ' fresh' : ''}" data-note-id="${n.id}">
            ${avatarHtml(n.author, 'note-avatar')}
            <div class="note-main">
                <div class="note-meta">
                    <span class="note-author">${esc(n.author)}</span>
                    <span class="note-time" data-ts="${n.created_at}" title="${esc(fullTime(n.created_at))}">${esc(relTime(n.created_at))}</span>
                    ${n.edited_at ? '<span class="note-edited">edited</span>' : ''}
                    ${canChange && !editing ? `<span class="note-actions">
                        <button data-action="note-edit">Edit</button><button data-action="note-delete">Delete</button></span>` : ''}
                </div>
                ${body}
            </div></div>`;
    }

    function notesFeedHtml(item) {
        return item.notes.length ? item.notes.map(noteHtml).join('') : '<div class="notes-empty">No notes yet — be the first to add one.</div>';
    }

    function cardFor(itemId) {
        return Array.from($('focus-list').children).find((c) => c.dataset && c.dataset.itemId === itemId) || null;
    }

    function renderNotesFeed(itemId, scrollToEnd) {
        const found = findItem(itemId);
        const card = cardFor(itemId);
        if (!found || !card) { S.fresh.clear(); return; }
        const feed = card.querySelector('.notes-feed');
        const nearBottom = feed.scrollHeight - feed.scrollTop - feed.clientHeight < 60;
        feed.innerHTML = notesFeedHtml(found.item);
        card.querySelector('.notes-count').textContent = found.item.notes.length;
        if (scrollToEnd || nearBottom) feed.scrollTop = feed.scrollHeight;
        if (S.fresh.size) {
            const ids = Array.from(S.fresh);
            setTimeout(() => ids.forEach((id) => S.fresh.delete(id)), 2500);
        }
    }

    function itemCardHtml(item) {
        const isSpot = S.spotlight && S.spotlight.item_id === item.id;
        const crit = item.criticality || 'normal';
        return `
        <div class="focus-item-card${isSpot ? ' is-spotlight' : ''}" data-item-id="${esc(item.id)}">
            <div class="focus-item-top">
                <div class="focus-item-info">
                    <h4>${esc(item.name)}</h4>
                    ${item.custom ? '<p class="sub-detail">Custom Focus Area</p>' : ''}
                </div>
                <div class="focus-item-actions">
                    <button class="btn-spotlight${isSpot ? ' active' : ''}" data-action="spotlight" title="Show this topic (name only) on the client screen">
                        ${ICONS.monitor}<span>${isSpot ? 'On client screen' : 'Show to client'}</span></button>
                    ${item.custom ? `
                        <button class="btn-edit-custom" data-action="rename" title="Rename custom focus item">${ICONS.pencil}</button>
                        <button class="btn-delete-custom" data-action="delete" title="Delete custom focus item">${ICONS.trash}</button>` : ''}
                    <button class="btn-suppress-item" data-action="suppress" title="Suppress requirement">${ICONS.x}</button>
                </div>
            </div>
            <div class="focus-controls">
                <div class="control-group"><label>Scope Status</label>
                    <div class="scope-selectors">
                        ${['in', 'nice', 'out'].map((s) => `<button class="scope-pill${item.scope === s ? ' active' : ''}" data-scope="${s}">${SCOPE_LABELS[s]}</button>`).join('')}
                    </div></div>
                <div class="control-group"><label>Priority</label>
                    <div class="priority-selectors">
                        ${['phase1', 'phase2', 'future'].map((p) => `<button class="priority-pill${item.priority === p ? ' active' : ''}" data-priority="${p}">${PRIORITY_LABELS[p]}</button>`).join('')}
                    </div></div>
                <div class="control-group"><label>Criticality</label>
                    <select class="criticality-select" data-val="${esc(crit)}">
                        <option value="super"${crit === 'super' ? ' selected' : ''}>Super Critical</option>
                        <option value="critical"${crit === 'critical' ? ' selected' : ''}>Critical</option>
                        <option value="normal"${crit === 'normal' ? ' selected' : ''}>Normal</option>
                    </select></div>
            </div>
            ${item.guidance ? `
            <div class="guidance-box">
                <div class="guidance-header-row">
                    <div class="guidance-title">Guidance Prompt <span style="opacity:.6;text-transform:none;letter-spacing:0">· team only</span></div>
                    <div class="guidance-actions" style="display:flex;gap:.5rem;">
                        <button class="btn-edit-guidance" data-action="edit-guidance" title="Edit guidance prompt">${ICONS.edit}<span>Edit</span></button>
                        <button class="btn-copy-guidance" data-action="guidance-to-note" title="Copy guidance into the note box">${ICONS.copy}<span>Use as note</span></button>
                    </div>
                </div>
                <div class="guidance-text">${esc(item.guidance)}</div>
            </div>` : ''}
            <div class="notes-wrapper">
                <div class="notes-head"><label>Notes <span class="notes-count">${item.notes.length}</span></label></div>
                <div class="notes-feed">${notesFeedHtml(item)}</div>
                <div class="note-compose">
                    <textarea class="notes-textarea" placeholder="Write a note, volume estimate, existing vendor detail…"></textarea>
                    <div class="note-compose-row">
                        <span class="note-compose-hint">Ctrl + Enter to push · visible to the team only</span>
                        <button class="btn-push-note" data-action="push-note">${ICONS.send}<span>Push note</span></button>
                    </div>
                </div>
            </div>
        </div>`;
    }

    function renderDrawerList() {
        const mod = findModule(S.activeModuleId);
        if (!mod) return;
        const list = $('focus-list');
        const content = document.querySelector('.drawer-content');
        const scrollTop = content.scrollTop;

        let keep = null;
        const ae = document.activeElement;
        if (ae && ae.classList && ae.classList.contains('notes-textarea')) {
            const c = ae.closest('.focus-item-card');
            if (c) keep = { id: c.dataset.itemId, start: ae.selectionStart, end: ae.selectionEnd };
        }

        const active = activeItemsOf(mod);
        const suppressed = mod.items.filter((i) => i.suppressed);

        if (!active.length) {
            list.innerHTML = '<p class="text-secondary" style="font-size:.9rem;text-align:center;padding:2rem;">No items yet. Add custom focus items below.</p>';
        } else {
            list.innerHTML = active.map(itemCardHtml).join('');
            Array.from(list.children).forEach((card) => {
                const ta = card.querySelector('.notes-textarea');
                if (ta) ta.value = S.drafts.get(card.dataset.itemId) || '';
                const feed = card.querySelector('.notes-feed');
                if (feed) feed.scrollTop = feed.scrollHeight;
            });
        }

        $('suppressed-items-section').style.display = suppressed.length ? 'block' : 'none';
        $('suppressed-count').textContent = suppressed.length;
        $('suppressed-list').innerHTML = suppressed.map((item) => `
            <div class="suppressed-item-row" data-item-id="${esc(item.id)}">
                <div class="suppressed-item-info"><h5>${esc(item.name)}</h5></div>
                <div class="suppressed-item-actions">
                    <button class="btn-restore-item" data-action="restore">Restore</button>
                    ${item.custom ? `<button class="btn-delete-suppressed" data-action="delete" title="Delete custom focus item">${ICONS.trash}</button>` : ''}
                </div>
            </div>`).join('');
        applySuppressedVisibility();

        content.scrollTop = scrollTop;
        if (keep) {
            const card = cardFor(keep.id);
            const ta = card && card.querySelector('.notes-textarea');
            if (ta) { ta.focus(); try { ta.setSelectionRange(keep.start, keep.end); } catch (e) { /* ignore */ } }
        }
    }

    function refreshItemControls(itemId) {
        const found = findItem(itemId);
        const card = cardFor(itemId);
        if (!found || !card) return;
        const it = found.item;
        card.querySelectorAll('.scope-pill').forEach((p) => p.classList.toggle('active', p.dataset.scope === it.scope));
        card.querySelectorAll('.priority-pill').forEach((p) => p.classList.toggle('active', p.dataset.priority === it.priority));
        const sel = card.querySelector('.criticality-select');
        sel.value = it.criticality; sel.dataset.val = it.criticality;
    }

    function refreshSpotlightButtons() {
        if (S.activeModuleId) renderDrawerHeader();
        Array.from($('focus-list').children).forEach((card) => {
            if (!card.dataset || !card.dataset.itemId) return;
            const on = !!(S.spotlight && S.spotlight.item_id === card.dataset.itemId);
            card.classList.toggle('is-spotlight', on);
            const btn = card.querySelector('.btn-spotlight');
            if (btn) {
                btn.classList.toggle('active', on);
                btn.querySelector('span').textContent = on ? 'On client screen' : 'Show to client';
            }
        });
    }

    function applySuppressedVisibility() {
        $('suppressed-list').style.display = S.suppressedOpen ? 'flex' : 'none';
        const btn = $('btn-toggle-suppressed');
        btn.classList.toggle('expanded', S.suppressedOpen);
        btn.querySelector('.toggle-text').textContent = S.suppressedOpen ? 'Hide' : 'Show';
    }

    // ---------------------------------------------------------------- actions
    async function patchItem(itemId, fields, message) {
        const found = findItem(itemId);
        if (!found) return;
        const before = {};
        Object.keys(fields).forEach((k) => { before[k] = found.item[k]; found.item[k] = fields[k]; });
        renderCards(); updateOverallProgress();
        if ('suppressed' in fields || 'name' in fields || 'guidance' in fields) renderDrawerList(); else refreshItemControls(itemId);
        updateDrawerSummary();
        try {
            const r = await api('PATCH', `/api/items/${encodeURIComponent(itemId)}`, fields);
            Object.assign(found.item, r.item);
            if (message) toast(message);
        } catch (e) {
            Object.assign(found.item, before);
            renderCards(); updateOverallProgress(); renderDrawerList(); updateDrawerSummary();
            toast(e.message);
        }
    }

    async function pushNote(itemId) {
        const card = cardFor(itemId);
        if (!card) return;
        const ta = card.querySelector('.notes-textarea');
        const btn = card.querySelector('[data-action="push-note"]');
        const text = ta.value.trim();
        if (!text) { ta.focus(); return; }
        btn.disabled = true;
        try {
            const r = await api('POST', `/api/items/${encodeURIComponent(itemId)}/notes`, { body: text });
            ta.value = ''; S.drafts.delete(itemId);
            const found = findItem(itemId);
            if (found && !found.item.notes.some((n) => n.id === r.note.id)) found.item.notes.push(r.note);
            renderNotesFeed(itemId, true);
            toast('Note pushed to the team');
        } catch (e) { toast(e.message); }
        btn.disabled = false;
        ta.focus();
    }

    async function saveNoteEdit(itemId) {
        if (!S.editing) return;
        const { noteId, text } = S.editing;
        try {
            const r = await api('PATCH', `/api/notes/${noteId}`, { body: text });
            const found = findItem(itemId);
            if (found) { const i = found.item.notes.findIndex((n) => n.id === noteId); if (i >= 0) found.item.notes[i] = r.note; }
            S.editing = null;
            renderNotesFeed(itemId);
        } catch (e) { toast(e.message); }
    }

    async function deleteNote(itemId, noteId) {
        if (!confirm('Delete this note?')) return;
        try {
            await api('DELETE', `/api/notes/${noteId}`);
            const found = findItem(itemId);
            if (found) found.item.notes = found.item.notes.filter((n) => n.id !== noteId);
            renderNotesFeed(itemId);
        } catch (e) { toast(e.message); }
    }

    function editGuidance(itemId, card) {
        const box = card.querySelector('.guidance-box');
        const textEl = box && box.querySelector('.guidance-text');
        if (!textEl || box.querySelector('.edit-guidance-wrapper')) return;
        const current = findItem(itemId).item.guidance;
        textEl.style.display = 'none';
        const wrap = document.createElement('div');
        wrap.className = 'edit-guidance-wrapper';
        wrap.innerHTML = `<textarea class="edit-guidance-textarea"></textarea>
            <div class="edit-guidance-btn-group">
                <button class="btn-secondary" style="padding:.35rem .75rem;font-size:.7rem">Cancel</button>
                <button class="btn-primary" style="padding:.35rem .75rem;font-size:.7rem">Save</button>
            </div>`;
        const ta = wrap.querySelector('textarea');
        ta.value = current;
        box.appendChild(wrap);
        ta.focus();
        const [cancel, save] = wrap.querySelectorAll('button');
        const done = () => { wrap.remove(); textEl.style.display = 'block'; };
        cancel.addEventListener('click', done);
        save.addEventListener('click', () => {
            const v = ta.value.trim();
            done();
            if (v && v !== current) patchItem(itemId, { guidance: v }, 'Guidance prompt updated');
        });
        ta.addEventListener('keydown', (e) => { if (e.key === 'Escape') done(); });
    }

    async function toggleSpotlight(target) {
        const sp = S.spotlight;
        const same = sp && (target.item_id ? sp.item_id === target.item_id : (sp.module_id === target.module_id && !sp.item_id));
        try { await api('PUT', '/api/spotlight', same ? {} : target); }
        catch (e) { toast(e.message); }
    }

    async function addCustomFocus() {
        const input = $('input-new-focus-name');
        const name = input.value.trim();
        if (!name || !S.activeModuleId) return;
        try {
            const r = await api('POST', `/api/modules/${encodeURIComponent(S.activeModuleId)}/items`, { name });
            input.value = '';
            const mod = findModule(S.activeModuleId);
            if (mod && !mod.items.some((i) => i.id === r.item.id)) mod.items.push(r.item);
            afterStructureChange(S.activeModuleId);
            toast(`Custom item "${name}" added!`);
        } catch (e) { toast(e.message); }
    }

    async function deleteItem(itemId) {
        const found = findItem(itemId);
        if (!found || !confirm(`Delete "${found.item.name}" and all of its notes?`)) return;
        try {
            await api('DELETE', `/api/items/${encodeURIComponent(itemId)}`);
            found.mod.items = found.mod.items.filter((i) => i.id !== itemId);
            S.drafts.delete(itemId);
            afterStructureChange(found.mod.id);
            toast(`Deleted "${found.item.name}"`);
        } catch (e) { toast(e.message); }
    }

    function renameItem(itemId) {
        const found = findItem(itemId);
        if (!found) return;
        const name = prompt('Rename focus item:', found.item.name);
        if (name && name.trim() && name.trim() !== found.item.name) patchItem(itemId, { name: name.trim() }, 'Renamed');
    }

    // ---------------------------------------------------------- module modal
    function openModuleModal(moduleId) {
        S.editingModuleId = moduleId;
        const mod = moduleId ? findModule(moduleId) : null;
        $('input-module-title').value = mod ? mod.title : '';
        $('input-module-desc').value = mod ? mod.description : '';
        document.querySelector('#add-module-modal .modal-header h3').textContent = mod ? 'Edit Custom Module' : 'Create Custom Module';
        $('btn-confirm-add-module').textContent = mod ? 'Save Changes' : 'Create Module';
        $('add-module-modal').classList.add('open');
        setTimeout(() => $('input-module-title').focus(), 100);
    }
    function closeModuleModal() { $('add-module-modal').classList.remove('open'); S.editingModuleId = null; }

    async function saveModule() {
        const title = $('input-module-title').value.trim();
        const description = $('input-module-desc').value.trim();
        if (!title) { alert('Please enter a module title.'); return; }
        try {
            if (S.editingModuleId) {
                const r = await api('PATCH', `/api/modules/${encodeURIComponent(S.editingModuleId)}`, { title, description });
                const mod = findModule(S.editingModuleId);
                if (mod) Object.assign(mod, { title: r.module.title, description: r.module.description });
                renderCards(); renderDrawerHeader();
                toast(`Module "${title}" updated`);
            } else {
                const r = await api('POST', '/api/modules', { title, description });
                if (!findModule(r.module.id)) S.modules.push(r.module);
                renderCards();
                toast(`Module "${title}" created`);
            }
            closeModuleModal();
        } catch (e) { toast(e.message); }
    }

    async function deleteModule(moduleId) {
        const mod = findModule(moduleId);
        if (!mod || !confirm(`Delete the module "${mod.title}", all its requirements and their notes? This can't be undone.`)) return;
        try {
            await api('DELETE', `/api/modules/${encodeURIComponent(moduleId)}`);
            S.modules = S.modules.filter((m) => m.id !== moduleId);
            closeDrawer(true); renderCards(); updateOverallProgress();
            toast(`Deleted module "${mod.title}"`);
        } catch (e) { toast(e.message); }
    }

    // ---------------------------------------------------------------- exports
    function noteLine(n) { return `[${n.author}, ${fullTime(n.created_at)}] ${n.body}`; }
    function companySlug() {
        const name = (S.company && S.company.name) ? S.company.name : 'requirement_gathering';
        return name.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '') || 'requirement_gathering';
    }

    function generateMarkdown() {
        const compName = (S.company && S.company.name) ? S.company.name : 'Requirement Gathering';
        const presetName = (S.company && S.company.preset_name) ? S.company.preset_name : '';
        let md = `# Requirement Gathering Report — ${compName}\n`;
        if (presetName) md += `**Industry Preset**: ${presetName}  \n`;
        md += `*Exported: ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()} by ${S.me.display_name}*\n\n`;
        let total = 0, scoped = 0;
        S.modules.forEach((m) => activeItemsOf(m).forEach((i) => { total++; if (i.scope !== 'pending') scoped++; }));
        const pct = total ? Math.round((scoped / total) * 100) : 0;
        md += `## Progress Summary: **${pct}% Complete** (${scoped} of ${total} items scoped)\n\n`;
        md += '| Module | Total Items | Scoped Items | Completion |\n| :--- | :---: | :---: | :---: |\n';
        S.modules.forEach((mod) => {
            const a = activeItemsOf(mod);
            const sc = a.filter((i) => i.scope !== 'pending').length;
            md += `| ${mod.title} | ${a.length} | ${sc} | ${a.length ? Math.round((sc / a.length) * 100) : 0}% |\n`;
        });
        md += '\n---\n\n';
        S.modules.forEach((mod) => {
            md += `## Module: ${mod.title}\n- **ID**: ${mod.id}\n`;
            if (mod.description) md += `- **Description**: ${mod.description}\n`;
            md += '\n';
            mod.items.forEach((item) => {
                md += `### Requirement: ${item.name}\n- **ID**: ${item.id}\n`;
                md += `- **Scope**: ${SCOPE_LABELS[item.scope] || item.scope}\n`;
                md += `- **Priority**: ${PRIORITY_LABELS[item.priority] || item.priority}\n`;
                md += `- **Criticality**: ${(item.criticality || 'normal').toUpperCase()}\n`;
                md += `- **Suppressed**: ${item.suppressed ? 'True' : 'False'}\n`;
                if (item.guidance) md += `- **Guidance**: ${item.guidance.replace(/\r?\n/g, ' ')}\n`;
                if (item.notes.length) md += `- **Notes**:\n${item.notes.map((n) => '  - ' + noteLine(n).replace(/\r?\n/g, '\n    ')).join('\n')}\n\n`;
                else md += '- **Notes**: None\n\n';
            });
            md += '---\n\n';
        });
        return md;
    }

    function exportCsv(cols) {
        const defs = [
            ['module', 'Module', (m) => m.title], ['id', 'Item ID', (m, i) => i.id], ['name', 'Item Name', (m, i) => i.name],
            ['guidance', 'Guidance Prompts', (m, i) => i.guidance || ''], ['scope', 'Scope Status', (m, i) => SCOPE_LABELS[i.scope] || i.scope],
            ['priority', 'Priority', (m, i) => PRIORITY_LABELS[i.priority] || i.priority],
            ['criticality', 'Criticality', (m, i) => (i.criticality || 'normal').toUpperCase()],
            ['notes', 'Notes', (m, i) => i.notes.map(noteLine).join('\n')],
        ].filter((d) => cols.includes(d[0]));
        if (!defs.length) { toast('Please select at least one column to export!'); return; }
        const cell = (v) => {
            let s = String(v == null ? '' : v).replace(/"/g, '""');
            return /[",\r\n]/.test(s) ? `"${s}"` : s;
        };
        const rows = [defs.map((d) => cell(d[1])).join(',')];
        S.modules.forEach((m) => m.items.forEach((i) => { if (!i.suppressed) rows.push(defs.map((d) => cell(d[2](m, i))).join(',')); }));
        download(`${companySlug()}_requirements.csv`, '\ufeff' + rows.join('\r\n'), 'text/csv;charset=utf-8;');
        toast('CSV downloaded (Excel ready)!');
    }

    function handleImportFile(ev) {
        const file = ev.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = async (e) => {
            try {
                const parsed = JSON.parse(e.target.result);
                const compName = (S.company && S.company.name) ? S.company.name : 'the active company';
                if (!confirm(`Importing REPLACES all current modules, requirements and notes for "${compName}". Continue?`)) return;
                const r = await api('POST', '/api/import', { modules: parsed });
                toast(`Imported ${r.modules} modules / ${r.items} requirements`);
            } catch (err) { alert('Import failed: ' + (err.message || 'invalid JSON file')); }
        };
        reader.readAsText(file);
    }

    async function resetAll() {
        const compName = (S.company && S.company.name) ? S.company.name : 'this company';
        const presetName = (S.company && S.company.preset_name) ? S.company.preset_name : 'the default preset';
        if (!confirm(`Reset ALL data for "${compName}"? This deletes every note, scope, priority and custom item for this company and restores the "${presetName}" preset. This cannot be undone.`)) return;
        try { await api('POST', '/api/reset'); toast(`Reset "${compName}" to preset.`); } catch (e) { toast(e.message); }
    }

    // --------------------------------------------------- companies & presets
    async function openCompaniesModal() {
        $('companies-modal').classList.add('open');
        try {
            const d = await api('GET', '/api/companies');
            S.company = d.active;
            S.companies = d.companies || [];
            S.presets = d.presets || [];
        } catch (e) { /* use cached state */ }
        renderCompaniesModal();
    }

    function closeCompaniesModal() {
        $('companies-modal').classList.remove('open');
    }

    function renderCompaniesModal() {
        const listEl = $('companies-list');
        if (listEl) {
            listEl.innerHTML = S.companies.map((c) => `
                <div class="company-row${c.is_active ? ' is-active' : ''}" data-company-id="${esc(c.id)}">
                    <div class="company-row-main">
                        <div class="company-row-title">
                            <strong>${esc(c.name)}</strong>
                            ${c.is_active ? '<span class="company-active-tag">Active on Workspace &amp; Client Screen</span>' : ''}
                            <span class="company-preset-tag">${esc(c.preset_name)}</span>
                        </div>
                        <div class="company-row-sub">
                            ${c.module_count} modules · ${c.scoped_items}/${c.total_items} requirements scoped (${c.progress_pct}%)
                        </div>
                    </div>
                    <div class="company-row-actions">
                        ${!c.is_active ? '<button class="primary" data-action="company-switch">Switch to Company</button>' : ''}
                        <button data-action="company-rename">Rename</button>
                        ${S.companies.length > 1 ? '<button class="danger" data-action="company-delete">Delete</button>' : ''}
                    </div>
                </div>`).join('');
        }
        const gridEl = $('presets-grid');
        if (gridEl) {
            gridEl.innerHTML = S.presets.map((p) => `
                <button type="button" class="preset-card${S.selectedPresetId === p.id ? ' selected' : ''}" data-preset-id="${esc(p.id)}">
                    <div>
                        <div class="preset-card-top">
                            <h5>${esc(p.name)}</h5>
                            <span class="preset-badge">${esc(p.badge)}</span>
                        </div>
                        <p>${esc(p.description)}</p>
                    </div>
                    <div class="preset-stats">${p.module_count} modules · ${p.item_count} focus items</div>
                </button>`).join('');
        }
    }

    async function switchCompany(companyId) {
        if (!companyId || (S.company && S.company.id === companyId)) return;
        try {
            const r = await api('PUT', '/api/companies/active', { company_id: companyId });
            if (S.activeModuleId) closeDrawer(true);
            await loadState();
            toast(`Switched to "${r.company.name}"`);
        } catch (e) { toast(e.message); }
    }

    async function createCompany() {
        const input = $('input-company-name');
        const name = input.value.trim();
        if (!name) {
            toast('Please enter a company / client name');
            input.focus();
            return;
        }
        const btn = $('btn-create-company');
        btn.disabled = true;
        try {
            const r = await api('POST', '/api/companies', {
                name,
                preset_id: S.selectedPresetId || 'metal_fabrication',
                switch_to: true,
            });
            input.value = '';
            if (S.activeModuleId) closeDrawer(true);
            await loadState();
            closeCompaniesModal();
            toast(`Created & switched to "${r.company.name}" (${r.company.preset_name})`);
        } catch (e) { toast(e.message); }
        btn.disabled = false;
    }

    async function renameCompany(companyId) {
        const comp = S.companies.find((c) => c.id === companyId);
        if (!comp) return;
        const next = prompt('Rename company:', comp.name);
        if (!next || !next.trim() || next.trim() === comp.name) return;
        try {
            await api('PATCH', `/api/companies/${encodeURIComponent(companyId)}`, { name: next.trim() });
            await loadState();
            toast('Company renamed');
        } catch (e) { toast(e.message); }
    }

    async function deleteCompany(companyId) {
        const comp = S.companies.find((c) => c.id === companyId);
        if (!comp) return;
        if (!confirm(`Delete company "${comp.name}" and all of its modules, requirements, and notes? This cannot be undone.`)) return;
        try {
            await api('DELETE', `/api/companies/${encodeURIComponent(companyId)}`);
            if (S.activeModuleId) closeDrawer(true);
            await loadState();
            toast(`Deleted "${comp.name}"`);
        } catch (e) { toast(e.message); }
    }

    // ------------------------------------------------------------------- team
    async function openTeam() {
        $('team-modal').classList.add('open');
        await renderTeam();
    }
    async function renderTeam() {
        try {
            const { users } = await api('GET', '/api/users');
            $('team-list').innerHTML = users.map((u) => `
                <div class="team-row" data-user-id="${u.id}">
                    ${avatarHtml(u.display_name, 'presence-avatar')}
                    <div class="team-row-info"><strong>${esc(u.display_name)}</strong><span>@${esc(u.username)}</span></div>
                    <span class="team-role-tag">${u.role === 'admin' ? 'Admin' : 'Member'}</span>
                    <button data-action="team-password">Reset password</button>
                    ${S.me.id !== u.id ? '<button class="danger" data-action="team-delete">Remove</button>' : ''}
                </div>`).join('');
        } catch (e) { toast(e.message); }
    }
    async function addTeamMember() {
        const body = {
            username: $('team-username').value.trim(), display_name: $('team-display').value.trim(),
            password: $('team-password').value, role: $('team-role').value,
        };
        try {
            await api('POST', '/api/users', body);
            ['team-username', 'team-display', 'team-password'].forEach((id) => { $(id).value = ''; });
            toast(`Added ${body.username}`);
            renderTeam();
        } catch (e) { toast(e.message); }
    }

    async function changeOwnPassword() {
        const current = prompt('Current password:');
        if (current === null) return;
        const next = prompt('New password (at least 8 characters):');
        if (next === null) return;
        try { await api('POST', '/api/me/password', { current, new: next }); toast('Password changed'); }
        catch (e) { toast(e.message); }
    }

    // ------------------------------------------------------- theme & font size
    function updateThemeUI(isLight) {
        document.querySelectorAll('.icon-theme-sun').forEach((el) => { el.style.display = isLight ? 'block' : 'none'; });
        document.querySelectorAll('.icon-theme-moon').forEach((el) => { el.style.display = isLight ? 'none' : 'block'; });
    }
    function toggleTheme() {
        const isLight = document.documentElement.classList.toggle('light-theme');
        localStorage.setItem('app_theme', isLight ? 'light' : 'dark');
        updateThemeUI(isLight);
    }
    function adjustFontScale(delta) {
        const cur = parseFloat(localStorage.getItem('font_scale') || '1.0');
        const next = Math.round(Math.max(0.8, Math.min(1.4, cur + delta)) * 10) / 10;
        if (next !== cur) {
            localStorage.setItem('font_scale', next.toFixed(1));
            document.documentElement.style.setProperty('--font-scale', next.toFixed(1));
            toast(`Font size set to ${Math.round(next * 100)}%`);
        }
    }

    // ------------------------------------------------------- event wiring
    function setupListeners() {
        // Login
        $('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = $('btn-login');
            btn.disabled = true;
            try {
                const r = await api('POST', '/api/login', { username: $('username').value.trim(), password: $('password').value });
                $('password').value = '';
                await enterApp(r.user);
            } catch (err) {
                const box = $('login-error');
                box.textContent = err.message; box.style.display = 'block';
                box.classList.remove('shake'); void box.offsetWidth; box.classList.add('shake');
            }
            btn.disabled = false;
        });
        $('btn-logout').addEventListener('click', async () => {
            if (!confirm('Are you sure you want to log out?')) return;
            try { await api('POST', '/api/logout'); } catch (e) { /* ignore */ }
            showLogin();
        });
        $('btn-change-password').addEventListener('click', changeOwnPassword);

        // Sidebar
        if (localStorage.getItem('sidebar_collapsed') === 'true') $('app-container').classList.add('sidebar-collapsed');
        $('btn-sidebar-toggle').addEventListener('click', () => {
            localStorage.setItem('sidebar_collapsed', $('app-container').classList.toggle('sidebar-collapsed'));
        });
        $('btn-mobile-menu').addEventListener('click', (e) => { e.stopPropagation(); $('sidebar').classList.toggle('open-mobile'); });
        document.addEventListener('click', (e) => {
            const sb = $('sidebar');
            if (sb.classList.contains('open-mobile') && !sb.contains(e.target) && !$('btn-mobile-menu').contains(e.target)) sb.classList.remove('open-mobile');
        });
        document.querySelectorAll('.nav-item').forEach((n) => n.addEventListener('click', () => $('sidebar').classList.remove('open-mobile')));

        // Client screen controls
        $('btn-client-screen').addEventListener('click', async () => {
            try { await api('PUT', '/api/client-screen', { hidden: !S.clientHidden }); } catch (e) { toast(e.message); }
        });
        $('btn-clear-spotlight').addEventListener('click', async () => {
            try { await api('PUT', '/api/spotlight', {}); } catch (e) { toast(e.message); }
        });

        // Drawer
        $('btn-close-drawer').addEventListener('click', () => closeDrawer());
        $('drawer-overlay').addEventListener('click', () => closeDrawer());
        $('suppressed-items-header').addEventListener('click', () => { S.suppressedOpen = !S.suppressedOpen; applySuppressedVisibility(); });
        $('btn-add-custom-focus').addEventListener('click', addCustomFocus);
        $('input-new-focus-name').addEventListener('keydown', (e) => { if (e.key === 'Enter') addCustomFocus(); });
        window.addEventListener('keydown', (e) => {
            if (e.key !== 'Escape') return;
            closeDrawer();
            ['export-modal', 'add-module-modal', 'csv-config-modal', 'team-modal', 'companies-modal'].forEach((id) => $(id).classList.remove('open'));
        });

        // Focus list - one delegated set of handlers, so live re-renders never lose wiring
        const list = $('focus-list');
        list.addEventListener('click', (e) => {
            const card = e.target.closest('.focus-item-card');
            if (!card) return;
            const itemId = card.dataset.itemId;
            const scopePill = e.target.closest('.scope-pill');
            if (scopePill) {
                const found = findItem(itemId);
                const scope = scopePill.dataset.scope;
                patchItem(itemId, { scope: found.item.scope === scope ? 'pending' : scope });
                return;
            }
            const prioPill = e.target.closest('.priority-pill');
            if (prioPill) { patchItem(itemId, { priority: prioPill.dataset.priority }); return; }
            const btn = e.target.closest('[data-action]');
            if (!btn) return;
            switch (btn.dataset.action) {
                case 'spotlight': toggleSpotlight({ module_id: S.activeModuleId, item_id: itemId }); break;
                case 'suppress': patchItem(itemId, { suppressed: true }, `Suppressed "${findItem(itemId).item.name}"`); break;
                case 'delete': deleteItem(itemId); break;
                case 'rename': renameItem(itemId); break;
                case 'edit-guidance': editGuidance(itemId, card); break;
                case 'guidance-to-note': {
                    const ta = card.querySelector('.notes-textarea');
                    const g = findItem(itemId).item.guidance;
                    ta.value = ta.value.trim() ? ta.value.trim() + '\n' + g : g;
                    S.drafts.set(itemId, ta.value); ta.focus();
                    break;
                }
                case 'push-note': pushNote(itemId); break;
                case 'note-edit': {
                    const noteId = Number(btn.closest('.note-entry').dataset.noteId);
                    const n = findItem(itemId).item.notes.find((x) => x.id === noteId);
                    if (n) { S.editing = { noteId, text: n.body }; renderNotesFeed(itemId); const t = card.querySelector('.note-edit-textarea'); if (t) t.focus(); }
                    break;
                }
                case 'note-cancel': S.editing = null; renderNotesFeed(itemId); break;
                case 'note-save': saveNoteEdit(itemId); break;
                case 'note-delete': deleteNote(itemId, Number(btn.closest('.note-entry').dataset.noteId)); break;
                default: break;
            }
        });
        list.addEventListener('change', (e) => {
            if (!e.target.classList.contains('criticality-select')) return;
            patchItem(e.target.closest('.focus-item-card').dataset.itemId, { criticality: e.target.value });
        });
        list.addEventListener('input', (e) => {
            const card = e.target.closest('.focus-item-card');
            if (!card) return;
            if (e.target.classList.contains('notes-textarea')) S.drafts.set(card.dataset.itemId, e.target.value);
            else if (e.target.classList.contains('note-edit-textarea') && S.editing) S.editing.text = e.target.value;
        });
        list.addEventListener('keydown', (e) => {
            const card = e.target.closest('.focus-item-card');
            if (!card) return;
            if (e.target.classList.contains('notes-textarea') && e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault(); pushNote(card.dataset.itemId);
            } else if (e.target.classList.contains('note-edit-textarea')) {
                if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); saveNoteEdit(card.dataset.itemId); }
                else if (e.key === 'Escape') { e.stopPropagation(); S.editing = null; renderNotesFeed(card.dataset.itemId); }
            }
        });
        $('suppressed-list').addEventListener('click', (e) => {
            const btn = e.target.closest('[data-action]');
            const row = e.target.closest('.suppressed-item-row');
            if (!btn || !row) return;
            const itemId = row.dataset.itemId;
            if (btn.dataset.action === 'restore') patchItem(itemId, { suppressed: false }, `Restored "${findItem(itemId).item.name}"`);
            else if (btn.dataset.action === 'delete') deleteItem(itemId);
        });

        // Exports / imports
        $('btn-export-md').addEventListener('click', () => { $('export-preview-content').value = generateMarkdown(); $('export-modal').classList.add('open'); });
        $('btn-close-export-modal').addEventListener('click', () => $('export-modal').classList.remove('open'));
        $('btn-copy-preview').addEventListener('click', () => {
            const ta = $('export-preview-content'); ta.select();
            navigator.clipboard.writeText(ta.value).then(() => toast('Copied to clipboard!'), () => alert('Copy failed — select the text manually.'));
        });
        $('btn-download-preview').addEventListener('click', () => { download(`${companySlug()}_requirements.md`, $('export-preview-content').value, 'text/markdown;charset=utf-8;'); toast('Markdown downloaded!'); });
        $('btn-export-json').addEventListener('click', () => { download(`${companySlug()}_requirements.json`, JSON.stringify(S.modules, null, 4), 'application/json;charset=utf-8;'); toast('JSON Config downloaded!'); });
        $('btn-import-json').addEventListener('click', () => { $('import-file-input').value = ''; $('import-file-input').click(); });
        $('import-file-input').addEventListener('change', handleImportFile);
        $('btn-export-csv').addEventListener('click', () => $('csv-config-modal').classList.add('open'));
        const closeCsv = () => $('csv-config-modal').classList.remove('open');
        $('btn-close-csv-modal').addEventListener('click', closeCsv);
        $('btn-cancel-csv').addEventListener('click', closeCsv);
        $('btn-confirm-export-csv').addEventListener('click', () => {
            exportCsv(Array.from(document.querySelectorAll('input[name="csv-col"]:checked')).map((c) => c.value));
            closeCsv();
        });
        $('btn-reset-data').addEventListener('click', resetAll);

        // Module modal
        $('btn-cancel-add-module').addEventListener('click', closeModuleModal);
        $('btn-close-add-module-modal').addEventListener('click', closeModuleModal);
        $('btn-confirm-add-module').addEventListener('click', saveModule);
        $('input-module-title').addEventListener('keydown', (e) => { if (e.key === 'Enter') saveModule(); });

        // Companies & Industry Presets modal
        $('btn-companies').addEventListener('click', openCompaniesModal);
        $('header-company-btn').addEventListener('click', openCompaniesModal);
        $('quick-company-select').addEventListener('change', (e) => switchCompany(e.target.value));
        $('btn-close-companies-modal').addEventListener('click', closeCompaniesModal);
        $('btn-companies-done').addEventListener('click', closeCompaniesModal);
        $('btn-create-company').addEventListener('click', createCompany);
        $('input-company-name').addEventListener('keydown', (e) => { if (e.key === 'Enter') createCompany(); });
        $('presets-grid').addEventListener('click', (e) => {
            const card = e.target.closest('.preset-card');
            if (!card) return;
            S.selectedPresetId = card.dataset.presetId;
            renderCompaniesModal();
        });
        $('companies-list').addEventListener('click', (e) => {
            const btn = e.target.closest('[data-action]');
            const row = e.target.closest('.company-row');
            if (!btn || !row) return;
            const cid = row.dataset.companyId;
            switch (btn.dataset.action) {
                case 'company-switch': switchCompany(cid); break;
                case 'company-rename': renameCompany(cid); break;
                case 'company-delete': deleteCompany(cid); break;
                default: break;
            }
        });

        // Team modal
        $('btn-team').addEventListener('click', openTeam);
        const closeTeam = () => $('team-modal').classList.remove('open');
        $('btn-close-team-modal').addEventListener('click', closeTeam);
        $('btn-team-done').addEventListener('click', closeTeam);
        $('btn-team-add').addEventListener('click', addTeamMember);
        $('team-list').addEventListener('click', async (e) => {
            const btn = e.target.closest('[data-action]');
            const row = e.target.closest('.team-row');
            if (!btn || !row) return;
            const id = row.dataset.userId;
            try {
                if (btn.dataset.action === 'team-delete') {
                    if (!confirm('Remove this team member? Their existing notes stay.')) return;
                    await api('DELETE', `/api/users/${id}`); renderTeam();
                } else if (btn.dataset.action === 'team-password') {
                    const pw = prompt('New password for this user (min 8 characters):');
                    if (pw) { await api('POST', `/api/users/${id}/password`, { password: pw }); toast('Password updated'); }
                }
            } catch (err) { toast(err.message); }
        });

        // Theme & font
        document.querySelectorAll('.btn-toggle-theme').forEach((b) => b.addEventListener('click', toggleTheme));
        document.querySelectorAll('.btn-increase-font').forEach((b) => b.addEventListener('click', () => adjustFontScale(0.1)));
        document.querySelectorAll('.btn-decrease-font').forEach((b) => b.addEventListener('click', () => adjustFontScale(-0.1)));
        updateThemeUI(document.documentElement.classList.contains('light-theme'));

        // Keep "5 min ago" labels fresh
        setInterval(() => {
            document.querySelectorAll('.note-time').forEach((el) => { el.textContent = relTime(Number(el.dataset.ts)); });
        }, 30000);
    }

    async function init() {
        setupListeners();
        try {
            const r = await api('GET', '/api/me');
            await enterApp(r.user);
        } catch (e) {
            showLogin();
        }
    }

    document.addEventListener('DOMContentLoaded', init);
})();
