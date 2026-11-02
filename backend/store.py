"""SQLite persistence layer for the Requirement Gathering server.

Design notes
------------
* One SQLite connection guarded by a re-entrant lock. Every public method is
  thread-safe, which is all the threaded HTTP server needs.
* Multi-company support: staff can create and switch between companies, each
  seeded from an industry preset (Metal Fab/Precision Eng, Injection Moulding,
  Food & Beverage, Pharma, Chemical, Electronics, Automotive/Aerospace, or Blank)
  with its own isolated modules, requirements, notes, and client spotlight.
* Notes are an *append-only log* (one row per note, with author + timestamp).
  Several people can push notes to the same requirement at the same moment
  without ever overwriting each other.
* Requirement fields (scope, priority, ...) are updated individually, so two
  people changing different fields of the same requirement don't clobber each
  other either.
* ``client_state()`` is the *only* thing the public client screen ever sees. It
  is built from an allow-list (names + a done/not-done flag) so notes,
  guidance prompts, priorities and criticality can never leak through it.
"""
import hashlib
import json
import os
import re
import secrets
import sqlite3
import threading
import time
from contextlib import contextmanager

from backend import presets

SCOPES = ("pending", "in", "nice", "out")
PRIORITIES = ("phase1", "phase2", "future")
CRITICALITIES = ("super", "critical", "normal")
ROLES = ("admin", "staff")

LEGACY_PRIORITY = {"high": "phase1", "med": "phase2", "medium": "phase2", "low": "future"}
LEGACY_CRITICALITY = {"high": "critical"}

DEFAULT_COMPANY_ID = "company-default"
DEFAULT_PRESET_ID = "metal_fabrication"
DEFAULT_PRESET_NAME = "Metal Fabrication & Precision Engineering"

DEFAULT_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 '
    '8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 '
    '8.967 0 00-6 2.292m0-14.25v14.25" /></svg>'
)

_SAFE_SVG_TAGS = {"svg", "path", "circle", "rect", "line", "polyline", "polygon", "g", "ellipse"}
_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{1,120}$")
_USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{2,40}$")

MAX_NOTE_LEN = 10000


class StoreError(Exception):
    """A problem the caller can show to the user (carries an HTTP status)."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


def _new_id(prefix):
    return "%s-%d-%s" % (prefix, int(time.time() * 1000), secrets.token_hex(2))


def _clean_id(value):
    if isinstance(value, str):
        value = value.strip()
        if _ID_RE.match(value):
            return value
    return None


def _safe_icon(value):
    """Icons are injected as raw HTML by the browser, so only allow plain SVG."""
    if not isinstance(value, str) or not value.strip():
        return DEFAULT_ICON
    value = value.strip()
    if len(value) > 6000:
        return DEFAULT_ICON
    tags = re.findall(r"<\s*/?\s*([A-Za-z0-9]+)", value)
    if not tags or any(t.lower() not in _SAFE_SVG_TAGS for t in tags):
        return DEFAULT_ICON
    if re.search(r"\son[a-z]+\s*=|javascript:|<\s*script", value, re.I):
        return DEFAULT_ICON
    if not value.lower().startswith("<svg"):
        return DEFAULT_ICON
    return value


def _hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _scoped_id(company_id, raw_id):
    """Ensure module and item IDs are unique per company in SQLite."""
    if not company_id or company_id == DEFAULT_COMPANY_ID:
        return raw_id
    prefix = "%s--" % company_id
    if raw_id.startswith(prefix):
        return raw_id
    return ("%s%s" % (prefix, raw_id))[:120]


def normalise_modules(raw, keep_state):
    """Validate a list of modules (seed file / JSON import) into canonical form.

    keep_state=False -> template mode: scope/priority/criticality/notes are reset.
    keep_state=True  -> import mode: they are preserved (legacy values are mapped).
    """
    if not isinstance(raw, list):
        raise StoreError("Expected a JSON array of modules.")
    now = time.time()
    modules, seen_modules, seen_items = [], set(), set()
    for m in raw:
        if not isinstance(m, dict):
            continue
        title = str(m.get("title", "")).strip()[:200]
        if not title:
            continue
        mid = _clean_id(m.get("id")) or _new_id("module-custom")
        if mid in seen_modules:
            mid = _new_id("module-custom")
        seen_modules.add(mid)
        items = []
        for it in m.get("items") or []:
            if not isinstance(it, dict):
                continue
            name = str(it.get("name", "")).strip()[:300]
            if not name:
                continue
            iid = _clean_id(it.get("id")) or _new_id("custom")
            if iid in seen_items:
                iid = "%s--%s" % (mid, iid)
                if iid in seen_items:
                    iid = _new_id("custom")
            seen_items.add(iid)
            entry = {
                "id": iid,
                "name": name,
                "guidance": str(it.get("guidance") or "")[:2000],
                "guidance_edited": bool(it.get("guidance_edited") or it.get("guidanceEdited")) if keep_state else False,
                "scope": "pending",
                "priority": "phase2",
                "criticality": "normal",
                "suppressed": False,
                "notes": [],
            }
            if keep_state:
                scope = it.get("scope")
                entry["scope"] = scope if scope in SCOPES else "pending"
                prio = LEGACY_PRIORITY.get(it.get("priority"), it.get("priority"))
                entry["priority"] = prio if prio in PRIORITIES else "phase2"
                crit = LEGACY_CRITICALITY.get(it.get("criticality"), it.get("criticality"))
                entry["criticality"] = crit if crit in CRITICALITIES else "normal"
                entry["suppressed"] = bool(it.get("suppressed"))
                entry["notes"] = _normalise_notes(it.get("notes"), now)
            items.append(entry)
        modules.append({
            "id": mid,
            "title": title,
            "description": str(m.get("description") or "")[:1000],
            "icon": _safe_icon(m.get("icon")),
            "items": items,
        })
    return modules


def _normalise_notes(raw, now):
    """Accept the legacy single-text 'notes' string or a list of note objects."""
    notes = []
    if isinstance(raw, str):
        if raw.strip():
            notes.append({"author": "Imported", "body": raw.strip()[:MAX_NOTE_LEN], "created_at": now, "edited_at": None})
    elif isinstance(raw, list):
        for n in raw:
            if not isinstance(n, dict):
                continue
            body = str(n.get("body", "")).strip()[:MAX_NOTE_LEN]
            if not body:
                continue
            created = n.get("created_at")
            edited = n.get("edited_at")
            notes.append({
                "author": str(n.get("author") or "Imported")[:60],
                "body": body,
                "created_at": float(created) if isinstance(created, (int, float)) else now,
                "edited_at": float(edited) if isinstance(edited, (int, float)) else None,
            })
    return notes


class Store:
    def __init__(self, db_path):
        self._lock = threading.RLock()
        self._db = sqlite3.connect(db_path, check_same_thread=False, isolation_level=None)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA foreign_keys=ON")
        self._db.execute("PRAGMA busy_timeout=5000")
        self._create_schema()

    # ------------------------------------------------------------------ infra
    def _create_schema(self):
        with self._lock:
            self._db.executescript(
                """
                CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    display_name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'staff',
                    created_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sessions(
                    token_hash TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS companies(
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    preset_id TEXT NOT NULL DEFAULT 'metal_fabrication',
                    preset_name TEXT NOT NULL DEFAULT 'Metal Fabrication & Precision Engineering',
                    spotlight TEXT NOT NULL DEFAULT '',
                    last_active_module_id TEXT NOT NULL DEFAULT '',
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS modules(
                    id TEXT PRIMARY KEY,
                    company_id TEXT NOT NULL DEFAULT 'company-default',
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    icon TEXT NOT NULL DEFAULT '',
                    position INTEGER NOT NULL,
                    is_custom INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS items(
                    id TEXT PRIMARY KEY,
                    module_id TEXT NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    guidance TEXT NOT NULL DEFAULT '',
                    guidance_edited INTEGER NOT NULL DEFAULT 0,
                    scope TEXT NOT NULL DEFAULT 'pending',
                    priority TEXT NOT NULL DEFAULT 'phase2',
                    criticality TEXT NOT NULL DEFAULT 'normal',
                    suppressed INTEGER NOT NULL DEFAULT 0,
                    position INTEGER NOT NULL,
                    is_custom INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS notes(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id TEXT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
                    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    author TEXT NOT NULL,
                    body TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    edited_at REAL
                );
                CREATE TABLE IF NOT EXISTS meta(
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_items_module ON items(module_id);
                CREATE INDEX IF NOT EXISTS idx_notes_item ON notes(item_id);
                """
            )
            # Non-destructive migration for existing databases created before multi-company support
            cols = {r["name"] for r in self._db.execute("PRAGMA table_info(modules)").fetchall()}
            if "company_id" not in cols:
                self._db.execute(
                    "ALTER TABLE modules ADD COLUMN company_id TEXT NOT NULL DEFAULT '%s'" % DEFAULT_COMPANY_ID
                )
            self._db.execute("CREATE INDEX IF NOT EXISTS idx_modules_company ON modules(company_id)")

            comp_cols = {r["name"] for r in self._db.execute("PRAGMA table_info(companies)").fetchall()}
            if "last_active_module_id" not in comp_cols:
                self._db.execute(
                    "ALTER TABLE companies ADD COLUMN last_active_module_id TEXT NOT NULL DEFAULT ''"
                )

    @contextmanager
    def _tx(self):
        with self._lock:
            self._db.execute("BEGIN IMMEDIATE")
            try:
                yield self._db
            except BaseException:
                self._db.execute("ROLLBACK")
                raise
            else:
                self._db.execute("COMMIT")

    def _all(self, sql, params=()):
        with self._lock:
            return self._db.execute(sql, params).fetchall()

    def _one(self, sql, params=()):
        with self._lock:
            return self._db.execute(sql, params).fetchone()

    # ------------------------------------------------------------------- meta
    def get_meta(self, key, default=None):
        row = self._one("SELECT value FROM meta WHERE key=?", (key,))
        return row["value"] if row else default

    def set_meta(self, key, value):
        with self._tx() as db:
            db.execute("INSERT INTO meta(key,value) VALUES(?,?) "
                       "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, str(value)))

    def secret_key(self):
        """Server-side secret (used to sign the optional client access cookie)."""
        key = self.get_meta("secret_key")
        if not key:
            key = secrets.token_hex(32)
            self.set_meta("secret_key", key)
        return key

    # -------------------------------------------------------------- companies
    def _ensure_default_company_row(self):
        with self._lock:
            count = self._one("SELECT COUNT(*) AS c FROM companies")["c"]
            if count == 0:
                now = time.time()
                old_spot = self.get_meta("spotlight", "") or ""
                with self._tx() as db:
                    db.execute(
                        "INSERT INTO companies(id,name,preset_id,preset_name,spotlight,last_active_module_id,created_at,updated_at) "
                        "VALUES(?,?,?,?,?,?,?,?)",
                        (
                            DEFAULT_COMPANY_ID,
                            "Precision Eng / Metal Fabricator",
                            DEFAULT_PRESET_ID,
                            DEFAULT_PRESET_NAME,
                            old_spot,
                            "",
                            now,
                            now,
                        ),
                    )
                    db.execute(
                        "INSERT INTO meta(key,value) VALUES('active_company_id',?) "
                        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                        (DEFAULT_COMPANY_ID,),
                    )

    def active_company_id(self):
        self._ensure_default_company_row()
        cid = self.get_meta("active_company_id")
        if cid and self._one("SELECT 1 FROM companies WHERE id=?", (cid,)):
            return cid
        first = self._one("SELECT id FROM companies ORDER BY created_at, rowid LIMIT 1")
        cid = first["id"] if first else DEFAULT_COMPANY_ID
        self.set_meta("active_company_id", cid)
        return cid

    def _company_stats(self, company_id):
        row = self._one(
            """
            SELECT
                (SELECT COUNT(*) FROM modules WHERE company_id=?) AS module_count,
                COUNT(i.id) AS total_items,
                 COALESCE(SUM(CASE WHEN i.scope != 'pending' THEN 1 ELSE 0 END), 0) AS scoped_items
            FROM modules m
            LEFT JOIN items i ON i.module_id = m.id AND i.suppressed = 0
            WHERE m.company_id = ?
            """,
            (company_id, company_id),
        )
        total = int(row["total_items"] or 0)
        scoped = int(row["scoped_items"] or 0)
        return {
            "module_count": int(row["module_count"] or 0),
            "total_items": total,
            "scoped_items": scoped,
            "progress_pct": int(round((scoped / total) * 100)) if total else 0,
        }

    def _company_dict(self, row, active_id=None):
        if active_id is None:
            active_id = self.active_company_id()
        stats = self._company_stats(row["id"])
        return {
            "id": row["id"],
            "name": row["name"],
            "preset_id": row["preset_id"],
            "preset_name": row["preset_name"],
            "is_active": row["id"] == active_id,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            **stats,
        }

    def get_active_company(self):
        cid = self.active_company_id()
        row = self._one("SELECT * FROM companies WHERE id=?", (cid,))
        return self._company_dict(row, cid) if row else None

    def list_companies(self):
        active_id = self.active_company_id()
        rows = self._all("SELECT * FROM companies ORDER BY created_at ASC, rowid ASC")
        return [self._company_dict(r, active_id) for r in rows]

    def create_company(self, name, preset_id=DEFAULT_PRESET_ID, seed_path=None, switch_to=True):
        name = (name or "").strip()[:120]
        if not name:
            raise StoreError("Please enter a company name.")
        preset = presets.PRESETS_BY_ID.get(preset_id)
        if not preset:
            raise StoreError("Unknown industry preset: %s" % preset_id)
        raw_modules = presets.get_preset_modules(preset_id, seed_path)
        modules = normalise_modules(raw_modules, keep_state=False) if raw_modules else []
        cid = _new_id("comp")
        now = time.time()
        first_mod_id = _scoped_id(cid, modules[0]["id"]) if modules else ""
        with self._tx() as db:
            db.execute(
                "INSERT INTO companies(id,name,preset_id,preset_name,spotlight,last_active_module_id,created_at,updated_at) "
                "VALUES(?,?,?,?,?,?,?,?)",
                (cid, name, preset["id"], preset["name"], "", first_mod_id, now, now),
            )
            for pos, module in enumerate(modules):
                self._insert_module(db, module, pos, company_id=cid)
            if switch_to:
                db.execute(
                    "INSERT INTO meta(key,value) VALUES('active_company_id',?) "
                    "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (cid,),
                )
        row = self._one("SELECT * FROM companies WHERE id=?", (cid,))
        return self._company_dict(row)

    def switch_company(self, company_id):
        company_id = (company_id or "").strip()
        row = self._one("SELECT * FROM companies WHERE id=?", (company_id,))
        if not row:
            raise StoreError("Company not found.", 404)
        self.set_meta("active_company_id", company_id)
        return self._company_dict(row, company_id)

    def update_company(self, company_id, name=None, preset_id=None, seed_path=None, apply_preset=False):
        company_id = (company_id or "").strip()
        row = self._one("SELECT * FROM companies WHERE id=?", (company_id,))
        if not row:
            raise StoreError("Company not found.", 404)
        new_name = (name if name is not None else row["name"]).strip()[:120]
        if not new_name:
            raise StoreError("Company name cannot be empty.")
        new_preset_id = preset_id or row["preset_id"]
        preset = presets.PRESETS_BY_ID.get(new_preset_id)
        if not preset:
            raise StoreError("Unknown industry preset: %s" % new_preset_id)
        now = time.time()
        with self._tx() as db:
            db.execute(
                "UPDATE companies SET name=?, preset_id=?, preset_name=?, updated_at=? WHERE id=?",
                (new_name, preset["id"], preset["name"], now, company_id),
            )
        if apply_preset:
            raw_modules = presets.get_preset_modules(preset["id"], seed_path)
            modules = normalise_modules(raw_modules, keep_state=False) if raw_modules else []
            self.replace_all(modules, company_id=company_id)
        updated = self._one("SELECT * FROM companies WHERE id=?", (company_id,))
        return self._company_dict(updated)

    def delete_company(self, company_id):
        company_id = (company_id or "").strip()
        with self._tx() as db:
            row = db.execute("SELECT * FROM companies WHERE id=?", (company_id,)).fetchone()
            if not row:
                raise StoreError("Company not found.", 404)
            total = db.execute("SELECT COUNT(*) AS c FROM companies").fetchone()["c"]
            if total <= 1:
                raise StoreError("You cannot delete the only remaining company.", 409)
            db.execute("DELETE FROM modules WHERE company_id=?", (company_id,))
            db.execute("DELETE FROM companies WHERE id=?", (company_id,))
            active = self.get_meta("active_company_id")
            if active == company_id:
                nxt = db.execute("SELECT id FROM companies ORDER BY created_at ASC, rowid ASC LIMIT 1").fetchone()
                if nxt:
                    db.execute(
                        "INSERT INTO meta(key,value) VALUES('active_company_id',?) "
                        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                        (nxt["id"],),
                    )
        return self.get_active_company()

    def _touch_company_module(self, db, company_id, module_id=None):
        now = time.time()
        if module_id:
            db.execute(
                "UPDATE companies SET last_active_module_id=?, updated_at=? WHERE id=?",
                (module_id, now, company_id),
            )
        else:
            db.execute("UPDATE companies SET updated_at=? WHERE id=?", (now, company_id))

    # ------------------------------------------------------------------ users
    @staticmethod
    def _user_dict(row):
        return {
            "id": row["id"],
            "username": row["username"],
            "display_name": row["display_name"],
            "role": row["role"],
            "created_at": row["created_at"],
        }

    def user_count(self):
        return self._one("SELECT COUNT(*) AS c FROM users")["c"]

    def create_user(self, username, password_hash, display_name="", role="staff"):
        username = (username or "").strip()
        if not _USERNAME_RE.match(username):
            raise StoreError("Username must be 2-40 characters: letters, numbers, dot, dash or underscore.")
        if role not in ROLES:
            raise StoreError("Invalid role.")
        display_name = (display_name or "").strip()[:60] or username
        try:
            with self._tx() as db:
                cur = db.execute(
                    "INSERT INTO users(username,display_name,password_hash,role,created_at) VALUES(?,?,?,?,?)",
                    (username, display_name, password_hash, role, time.time()))
                user_id = cur.lastrowid
        except sqlite3.IntegrityError:
            raise StoreError("That username is already taken.", 409)
        return self.get_user(user_id)

    def get_user(self, user_id):
        row = self._one("SELECT * FROM users WHERE id=?", (user_id,))
        return self._user_dict(row) if row else None

    def get_user_for_login(self, username):
        """Returns (user_dict, password_hash) or (None, None)."""
        row = self._one("SELECT * FROM users WHERE username=?", ((username or "").strip(),))
        if not row:
            return None, None
        return self._user_dict(row), row["password_hash"]

    def list_users(self):
        return [self._user_dict(r) for r in self._all("SELECT * FROM users ORDER BY username COLLATE NOCASE")]

    def delete_user(self, user_id):
        with self._tx() as db:
            row = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
            if not row:
                raise StoreError("User not found.", 404)
            if row["role"] == "admin":
                admins = db.execute("SELECT COUNT(*) AS c FROM users WHERE role='admin'").fetchone()["c"]
                if admins <= 1:
                    raise StoreError("You can't remove the last administrator.", 409)
            db.execute("DELETE FROM users WHERE id=?", (user_id,))

    def set_password_hash(self, user_id, password_hash):
        with self._tx() as db:
            cur = db.execute("UPDATE users SET password_hash=? WHERE id=?", (password_hash, user_id))
            if cur.rowcount == 0:
                raise StoreError("User not found.", 404)
            db.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))

    # --------------------------------------------------------------- sessions
    def create_session(self, user_id, ttl_seconds):
        token = secrets.token_urlsafe(32)
        now = time.time()
        with self._tx() as db:
            db.execute("DELETE FROM sessions WHERE expires_at < ?", (now,))
            db.execute("INSERT INTO sessions(token_hash,user_id,created_at,expires_at) VALUES(?,?,?,?)",
                       (_hash_token(token), user_id, now, now + ttl_seconds))
        return token

    def user_for_session(self, token):
        if not token:
            return None
        row = self._one(
            "SELECT u.* FROM sessions s JOIN users u ON u.id = s.user_id "
            "WHERE s.token_hash=? AND s.expires_at > ?", (_hash_token(token), time.time()))
        return self._user_dict(row) if row else None

    def delete_session(self, token):
        if not token:
            return
        with self._tx() as db:
            db.execute("DELETE FROM sessions WHERE token_hash=?", (_hash_token(token),))

    # ------------------------------------------------------------- row mapping
    @staticmethod
    def _module_dict(row):
        return {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "icon": row["icon"],
            "custom": bool(row["is_custom"]),
        }

    @staticmethod
    def _item_dict(row):
        return {
            "id": row["id"],
            "module_id": row["module_id"],
            "name": row["name"],
            "guidance": row["guidance"],
            "guidance_edited": bool(row["guidance_edited"]),
            "scope": row["scope"],
            "priority": row["priority"],
            "criticality": row["criticality"],
            "suppressed": bool(row["suppressed"]),
            "custom": bool(row["is_custom"]),
        }

    @staticmethod
    def _note_dict(row):
        return {
            "id": row["id"],
            "item_id": row["item_id"],
            "user_id": row["user_id"],
            "author": row["author"],
            "body": row["body"],
            "created_at": row["created_at"],
            "edited_at": row["edited_at"],
        }

    # ------------------------------------------------------------ bulk (re)load
    def _insert_module(self, db, module, position, company_id=None):
        cid = company_id or self.active_company_id()
        raw_mid = module["id"]
        is_custom_mod = 1 if ("module-custom-" in raw_mid) else 0
        mid = _scoped_id(cid, raw_mid)
        db.execute(
            "INSERT INTO modules(id,company_id,title,description,icon,position,is_custom) VALUES(?,?,?,?,?,?,?)",
            (mid, cid, module["title"], module["description"], module["icon"], position, is_custom_mod),
        )
        for i, it in enumerate(module["items"]):
            raw_iid = it["id"]
            is_custom_item = 1 if (raw_iid.startswith("custom-") or "--custom-" in raw_iid) else 0
            iid = _scoped_id(cid, raw_iid)
            db.execute(
                "INSERT INTO items(id,module_id,name,guidance,guidance_edited,scope,priority,criticality,"
                "suppressed,position,is_custom) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (
                    iid,
                    mid,
                    it["name"],
                    it["guidance"],
                    1 if it["guidance_edited"] else 0,
                    it["scope"],
                    it["priority"],
                    it["criticality"],
                    1 if it["suppressed"] else 0,
                    i,
                    is_custom_item,
                ),
            )
            for n in it["notes"]:
                db.execute(
                    "INSERT INTO notes(item_id,user_id,author,body,created_at,edited_at) VALUES(?,?,?,?,?,?)",
                    (iid, None, n["author"], n["body"], n["created_at"], n["edited_at"]),
                )

    def replace_all(self, modules, company_id=None):
        """Wipe every module/requirement/note for `company_id` (or active company) and load `modules`."""
        cid = company_id or self.active_company_id()
        first_mod_id = _scoped_id(cid, modules[0]["id"]) if modules else ""
        with self._tx() as db:
            db.execute("DELETE FROM modules WHERE company_id=?", (cid,))
            for pos, module in enumerate(modules):
                self._insert_module(db, module, pos, company_id=cid)
            db.execute(
                "UPDATE companies SET spotlight='', last_active_module_id=?, updated_at=? WHERE id=?",
                (first_mod_id, time.time(), cid),
            )

    def import_modules(self, raw):
        modules = normalise_modules(raw, keep_state=True)
        if not modules:
            raise StoreError("No modules found in that file.")
        self.replace_all(modules)
        return len(modules), sum(len(m["items"]) for m in modules)

    def load_seed_file(self, path):
        with open(path, "r", encoding="utf-8-sig") as fh:
            raw = json.load(fh)
        return normalise_modules(raw, keep_state=False)

    def ensure_seeded(self, seed_path):
        """Seed the template on first run only. Returns a human-readable status."""
        self._ensure_default_company_row()
        if self.get_meta("seeded"):
            return "existing data"
        if self._one("SELECT COUNT(*) AS c FROM modules")["c"] > 0:
            self.set_meta("seeded", "1")
            return "existing data"
        if not seed_path or not os.path.exists(seed_path):
            return "no seed file found (%s) - starting empty; import a JSON config from the Admin menu" % seed_path
        modules = self.load_seed_file(seed_path)
        self.replace_all(modules, company_id=DEFAULT_COMPANY_ID)
        self.set_meta("seeded", "1")
        return "seeded %d modules from %s" % (len(modules), os.path.basename(seed_path))

    def reset_to_seed(self, seed_path):
        comp = self.get_active_company()
        preset_id = comp["preset_id"] if comp else DEFAULT_PRESET_ID
        raw_modules = presets.get_preset_modules(preset_id, seed_path)
        if not raw_modules and preset_id != "blank":
            if not seed_path or not os.path.exists(seed_path):
                raise StoreError("Seed file not found on the server: %s" % seed_path, 500)
            modules = self.load_seed_file(seed_path)
        else:
            modules = normalise_modules(raw_modules, keep_state=False) if raw_modules else []
        self.replace_all(modules, company_id=comp["id"] if comp else DEFAULT_COMPANY_ID)

    # ------------------------------------------------------------------ state
    def get_state(self, seed_path=None):
        """Full staff-side state for the active company, with companies & presets list."""
        with self._lock:
            cid = self.active_company_id()
            modules = [
                self._module_dict(r)
                for r in self._db.execute(
                    "SELECT * FROM modules WHERE company_id=? ORDER BY position, rowid", (cid,)
                ).fetchall()
            ]
            by_module = {}
            for m in modules:
                m["items"] = []
                by_module[m["id"]] = m
            by_item = {}
            if by_module:
                for r in self._db.execute(
                    "SELECT i.* FROM items i JOIN modules m ON m.id = i.module_id "
                    "WHERE m.company_id=? ORDER BY i.position, i.rowid",
                    (cid,),
                ).fetchall():
                    item = self._item_dict(r)
                    item["notes"] = []
                    by_item[item["id"]] = item
                    if item["module_id"] in by_module:
                        by_module[item["module_id"]]["items"].append(item)
                for r in self._db.execute(
                    "SELECT n.* FROM notes n JOIN items i ON i.id = n.item_id "
                    "JOIN modules m ON m.id = i.module_id WHERE m.company_id=? ORDER BY n.created_at, n.id",
                    (cid,),
                ).fetchall():
                    if r["item_id"] in by_item:
                        by_item[r["item_id"]]["notes"].append(self._note_dict(r))
            return {
                "company": self.get_active_company(),
                "companies": self.list_companies(),
                "presets": presets.list_presets(seed_path),
                "modules": modules,
                "spotlight": self.get_spotlight(),
                "client_hidden": self.get_client_hidden(),
            }

    def client_state(self):
        """What the public client screen may see. Built from an allow-list on purpose."""
        with self._lock:
            hidden = self.get_client_hidden()
            if hidden:
                return {"hidden": True}
            cid = self.active_company_id()
            comp_row = self._one("SELECT * FROM companies WHERE id=?", (cid,))
            modules, done_total, all_total = [], 0, 0
            module_rows = self._db.execute(
                "SELECT * FROM modules WHERE company_id=? ORDER BY position, rowid", (cid,)
            ).fetchall()
            item_rows = self._db.execute(
                "SELECT i.id, i.module_id, i.name, i.scope FROM items i "
                "JOIN modules m ON m.id = i.module_id "
                "WHERE m.company_id=? AND i.suppressed=0 ORDER BY i.position, i.rowid",
                (cid,),
            ).fetchall()
            items_by_module = {}
            for r in item_rows:
                items_by_module.setdefault(r["module_id"], []).append(
                    {"id": r["id"], "name": r["name"], "done": r["scope"] != "pending"}
                )
            names = {}
            for r in module_rows:
                items = items_by_module.get(r["id"], [])
                done = sum(1 for i in items if i["done"])
                done_total += done
                all_total += len(items)
                names[r["id"]] = r["title"]
                modules.append({
                    "id": r["id"],
                    "title": r["title"],
                    "description": r["description"],
                    "icon": r["icon"],
                    "done": done,
                    "total": len(items),
                    "items": items,
                })
            spotlight = None
            sp = self.get_spotlight()
            if sp and sp["module_id"] in names:
                item_name = None
                if sp.get("item_id"):
                    for i in items_by_module.get(sp["module_id"], []):
                        if i["id"] == sp["item_id"]:
                            item_name = i["name"]
                    if item_name is None:  # item suppressed/deleted -> fall back to module
                        sp["item_id"] = None
                spotlight = {
                    "module_id": sp["module_id"],
                    "module_title": names[sp["module_id"]],
                    "item_id": sp.get("item_id"),
                    "item_name": item_name,
                }
            # Determine the active module to keep pinned at the top of the client screen:
            # 1) Explicit spotlight module, or 2) Most recently active module in this company
            active_module_id = None
            if spotlight:
                active_module_id = spotlight["module_id"]
            elif comp_row and comp_row["last_active_module_id"] in names:
                active_module_id = comp_row["last_active_module_id"]

            return {
                "hidden": False,
                "company": {
                    "id": comp_row["id"],
                    "name": comp_row["name"],
                    "preset_name": comp_row["preset_name"],
                } if comp_row else None,
                "modules": modules,
                "progress": {"done": done_total, "total": all_total},
                "spotlight": spotlight,
                "active_module_id": active_module_id,
            }

    # ------------------------------------------------- spotlight / client screen
    def get_spotlight(self):
        cid = self.active_company_id()
        row = self._one("SELECT spotlight FROM companies WHERE id=?", (cid,))
        raw = row["spotlight"] if row else ""
        if not raw:
            return None
        try:
            data = json.loads(raw)
        except ValueError:
            return None
        if isinstance(data, dict) and data.get("module_id"):
            return {"module_id": data["module_id"], "item_id": data.get("item_id")}
        return None

    def set_spotlight(self, module_id=None, item_id=None):
        cid = self.active_company_id()
        if item_id:
            row = self._one(
                "SELECT i.module_id FROM items i JOIN modules m ON m.id = i.module_id WHERE i.id=? AND m.company_id=?",
                (item_id, cid),
            )
            if not row:
                raise StoreError("Requirement not found.", 404)
            module_id = row["module_id"]
        elif module_id:
            if not self._one("SELECT 1 FROM modules WHERE id=? AND company_id=?", (module_id, cid)):
                raise StoreError("Module not found.", 404)
        with self._tx() as db:
            if not module_id:
                db.execute("UPDATE companies SET spotlight='' WHERE id=?", (cid,))
                return None
            value = {"module_id": module_id, "item_id": item_id or None}
            db.execute(
                "UPDATE companies SET spotlight=?, last_active_module_id=?, updated_at=? WHERE id=?",
                (json.dumps(value), module_id, time.time(), cid),
            )
            return value

    def get_client_hidden(self):
        return self.get_meta("client_hidden", "0") == "1"

    def set_client_hidden(self, hidden):
        self.set_meta("client_hidden", "1" if hidden else "0")
        return bool(hidden)

    # ---------------------------------------------------------------- modules
    def create_module(self, title, description=""):
        title = (title or "").strip()[:200]
        if not title:
            raise StoreError("Please enter a module title.")
        description = (description or "").strip()[:1000] or "Custom business module configuration."
        cid = self.active_company_id()
        mid = _new_id("module-custom")
        with self._tx() as db:
            pos = db.execute(
                "SELECT COALESCE(MAX(position), -1) + 1 AS p FROM modules WHERE company_id=?", (cid,)
            ).fetchone()["p"]
            db.execute(
                "INSERT INTO modules(id,company_id,title,description,icon,position,is_custom) VALUES(?,?,?,?,?,?,1)",
                (mid, cid, title, description, DEFAULT_ICON, pos),
            )
            self._touch_company_module(db, cid, mid)
            row = db.execute("SELECT * FROM modules WHERE id=?", (mid,)).fetchone()
        module = self._module_dict(row)
        module["items"] = []
        return module

    def update_module(self, module_id, title, description):
        title = (title or "").strip()[:200]
        if not title:
            raise StoreError("Please enter a module title.")
        description = (description or "").strip()[:1000] or "Custom business module configuration."
        cid = self.active_company_id()
        with self._tx() as db:
            row = db.execute("SELECT * FROM modules WHERE id=? AND company_id=?", (module_id, cid)).fetchone()
            if not row:
                raise StoreError("Module not found.", 404)
            if not row["is_custom"]:
                raise StoreError("Only custom modules can be edited.", 403)
            db.execute("UPDATE modules SET title=?, description=? WHERE id=?", (title, description, module_id))
            self._touch_company_module(db, cid, module_id)
            row = db.execute("SELECT * FROM modules WHERE id=?", (module_id,)).fetchone()
        return self._module_dict(row)

    def delete_module(self, module_id):
        cid = self.active_company_id()
        with self._tx() as db:
            row = db.execute("SELECT * FROM modules WHERE id=? AND company_id=?", (module_id, cid)).fetchone()
            if not row:
                raise StoreError("Module not found.", 404)
            if not row["is_custom"]:
                raise StoreError("Only custom modules can be deleted.", 403)
            db.execute("DELETE FROM modules WHERE id=?", (module_id,))
            sp = self.get_spotlight()
            if sp and sp["module_id"] == module_id:
                db.execute("UPDATE companies SET spotlight='' WHERE id=?", (cid,))

    # ------------------------------------------------------------ requirements
    def create_item(self, module_id, name):
        name = (name or "").strip()[:300]
        if not name:
            raise StoreError("Please enter a name.")
        cid = self.active_company_id()
        iid = _new_id("custom")
        with self._tx() as db:
            if not db.execute("SELECT 1 FROM modules WHERE id=? AND company_id=?", (module_id, cid)).fetchone():
                raise StoreError("Module not found.", 404)
            pos = db.execute("SELECT COALESCE(MAX(position), -1) + 1 AS p FROM items WHERE module_id=?",
                             (module_id,)).fetchone()["p"]
            db.execute(
                "INSERT INTO items(id,module_id,name,guidance,guidance_edited,scope,priority,criticality,"
                "suppressed,position,is_custom) VALUES(?,?,?,?,0,'pending','phase2','normal',0,?,1)",
                (iid, module_id, name, "Custom focus item added by user.", pos))
            self._touch_company_module(db, cid, module_id)
            row = db.execute("SELECT * FROM items WHERE id=?", (iid,)).fetchone()
        item = self._item_dict(row)
        item["notes"] = []
        return item

    def get_item(self, item_id):
        row = self._one("SELECT * FROM items WHERE id=?", (item_id,))
        return self._item_dict(row) if row else None

    def update_item(self, item_id, fields):
        allowed = {"scope", "priority", "criticality", "suppressed", "name", "guidance"}
        unknown = set(fields) - allowed
        if unknown:
            raise StoreError("Unknown field: %s" % ", ".join(sorted(unknown)))
        cid = self.active_company_id()
        with self._tx() as db:
            row = db.execute(
                "SELECT i.* FROM items i JOIN modules m ON m.id = i.module_id WHERE i.id=? AND m.company_id=?",
                (item_id, cid),
            ).fetchone()
            if not row:
                raise StoreError("Requirement not found.", 404)
            sets, vals = [], []
            for key, options in (("scope", SCOPES), ("priority", PRIORITIES), ("criticality", CRITICALITIES)):
                if key in fields:
                    if not isinstance(fields[key], str) or fields[key] not in options:
                        raise StoreError("Invalid %s." % key)
                    sets.append("%s=?" % key)
                    vals.append(fields[key])
            if "suppressed" in fields:
                if not isinstance(fields["suppressed"], bool):
                    raise StoreError("Invalid suppressed flag.")
                sets.append("suppressed=?")
                vals.append(1 if fields["suppressed"] else 0)
            if "name" in fields:
                if not row["is_custom"]:
                    raise StoreError("Only custom requirements can be renamed.", 403)
                name = str(fields["name"] or "").strip()[:300]
                if not name:
                    raise StoreError("Name can't be empty.")
                sets.append("name=?")
                vals.append(name)
            if "guidance" in fields:
                guidance = str(fields["guidance"] or "").strip()[:2000]
                if not guidance:
                    raise StoreError("Guidance can't be empty.")
                sets.append("guidance=?")
                vals.append(guidance)
                sets.append("guidance_edited=1")
            if sets:
                db.execute("UPDATE items SET %s WHERE id=?" % ", ".join(sets), vals + [item_id])
                self._touch_company_module(db, cid, row["module_id"])
                row = db.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
        return self._item_dict(row)

    def delete_item(self, item_id):
        cid = self.active_company_id()
        with self._tx() as db:
            row = db.execute(
                "SELECT i.* FROM items i JOIN modules m ON m.id = i.module_id WHERE i.id=? AND m.company_id=?",
                (item_id, cid),
            ).fetchone()
            if not row:
                raise StoreError("Requirement not found.", 404)
            if not row["is_custom"]:
                raise StoreError("Only custom requirements can be deleted.", 403)
            db.execute("DELETE FROM items WHERE id=?", (item_id,))
        sp = self.get_spotlight()
        if sp and sp.get("item_id") == item_id:
            self.set_spotlight(sp["module_id"], None)
        return dict(self._item_dict(row))

    # ------------------------------------------------------------------ notes
    @staticmethod
    def _clean_body(body):
        body = (body if isinstance(body, str) else "").strip()
        if not body:
            raise StoreError("A note can't be empty.")
        if len(body) > MAX_NOTE_LEN:
            raise StoreError("That note is too long (max %d characters)." % MAX_NOTE_LEN)
        return body

    def add_note(self, item_id, user, body):
        body = self._clean_body(body)
        cid = self.active_company_id()
        with self._tx() as db:
            item_row = db.execute(
                "SELECT i.module_id FROM items i JOIN modules m ON m.id = i.module_id WHERE i.id=? AND m.company_id=?",
                (item_id, cid),
            ).fetchone()
            if not item_row:
                raise StoreError("Requirement not found.", 404)
            cur = db.execute(
                "INSERT INTO notes(item_id,user_id,author,body,created_at,edited_at) VALUES(?,?,?,?,?,NULL)",
                (item_id, user["id"], user["display_name"], body, time.time()))
            self._touch_company_module(db, cid, item_row["module_id"])
            row = db.execute("SELECT * FROM notes WHERE id=?", (cur.lastrowid,)).fetchone()
        return self._note_dict(row)

    def _note_for_change(self, db, note_id, user):
        row = db.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()
        if not row:
            raise StoreError("Note not found.", 404)
        if user["role"] != "admin" and row["user_id"] != user["id"]:
            raise StoreError("You can only change your own notes.", 403)
        return row

    def edit_note(self, note_id, user, body):
        body = self._clean_body(body)
        with self._tx() as db:
            self._note_for_change(db, note_id, user)
            db.execute("UPDATE notes SET body=?, edited_at=? WHERE id=?", (body, time.time(), note_id))
            row = db.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()
        return self._note_dict(row)

    def delete_note(self, note_id, user):
        with self._tx() as db:
            row = self._note_for_change(db, note_id, user)
            db.execute("DELETE FROM notes WHERE id=?", (note_id,))
        return self._note_dict(row)
