"""SQLite persistence layer for the Requirement Gathering server.

Design notes
------------
* One SQLite connection guarded by a re-entrant lock. Every public method is
  thread-safe, which is all the threaded HTTP server needs.
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

SCOPES = ("pending", "in", "nice", "out")
PRIORITIES = ("phase1", "phase2", "future")
CRITICALITIES = ("super", "critical", "normal")
ROLES = ("admin", "staff")

LEGACY_PRIORITY = {"high": "phase1", "med": "phase2", "medium": "phase2", "low": "future"}
LEGACY_CRITICALITY = {"high": "critical"}

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
                CREATE TABLE IF NOT EXISTS modules(
                    id TEXT PRIMARY KEY,
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
    def _insert_module(self, db, module, position):
        db.execute("INSERT INTO modules(id,title,description,icon,position,is_custom) VALUES(?,?,?,?,?,?)",
                   (module["id"], module["title"], module["description"], module["icon"], position,
                    1 if module["id"].startswith("module-custom-") else 0))
        for i, it in enumerate(module["items"]):
            db.execute(
                "INSERT INTO items(id,module_id,name,guidance,guidance_edited,scope,priority,criticality,"
                "suppressed,position,is_custom) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (it["id"], module["id"], it["name"], it["guidance"], 1 if it["guidance_edited"] else 0,
                 it["scope"], it["priority"], it["criticality"], 1 if it["suppressed"] else 0, i,
                 1 if it["id"].startswith("custom-") else 0))
            for n in it["notes"]:
                db.execute("INSERT INTO notes(item_id,user_id,author,body,created_at,edited_at) VALUES(?,?,?,?,?,?)",
                           (it["id"], None, n["author"], n["body"], n["created_at"], n["edited_at"]))

    def replace_all(self, modules):
        """Wipe every module/requirement/note and load `modules` (already normalised)."""
        with self._tx() as db:
            db.execute("DELETE FROM notes")
            db.execute("DELETE FROM items")
            db.execute("DELETE FROM modules")
            for pos, module in enumerate(modules):
                self._insert_module(db, module, pos)
            db.execute("INSERT INTO meta(key,value) VALUES('spotlight','') "
                       "ON CONFLICT(key) DO UPDATE SET value=''")

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
        if self.get_meta("seeded"):
            return "existing data"
        if self._one("SELECT COUNT(*) AS c FROM modules")["c"] > 0:
            self.set_meta("seeded", "1")
            return "existing data"
        if not seed_path or not os.path.exists(seed_path):
            return "no seed file found (%s) - starting empty; import a JSON config from the Admin menu" % seed_path
        modules = self.load_seed_file(seed_path)
        self.replace_all(modules)
        self.set_meta("seeded", "1")
        return "seeded %d modules from %s" % (len(modules), os.path.basename(seed_path))

    def reset_to_seed(self, seed_path):
        if not seed_path or not os.path.exists(seed_path):
            raise StoreError("Seed file not found on the server: %s" % seed_path, 500)
        self.replace_all(self.load_seed_file(seed_path))

    # ------------------------------------------------------------------ state
    def get_state(self):
        """Full staff-side state, with every note attached to its requirement."""
        with self._lock:
            modules = [self._module_dict(r) for r in
                       self._db.execute("SELECT * FROM modules ORDER BY position, rowid").fetchall()]
            by_module = {}
            for m in modules:
                m["items"] = []
                by_module[m["id"]] = m
            by_item = {}
            for r in self._db.execute("SELECT * FROM items ORDER BY position, rowid").fetchall():
                item = self._item_dict(r)
                item["notes"] = []
                by_item[item["id"]] = item
                if item["module_id"] in by_module:
                    by_module[item["module_id"]]["items"].append(item)
            for r in self._db.execute("SELECT * FROM notes ORDER BY created_at, id").fetchall():
                if r["item_id"] in by_item:
                    by_item[r["item_id"]]["notes"].append(self._note_dict(r))
            return {
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
            modules, done_total, all_total = [], 0, 0
            module_rows = self._db.execute("SELECT * FROM modules ORDER BY position, rowid").fetchall()
            item_rows = self._db.execute(
                "SELECT id, module_id, name, scope FROM items WHERE suppressed=0 ORDER BY position, rowid").fetchall()
            items_by_module = {}
            for r in item_rows:
                items_by_module.setdefault(r["module_id"], []).append(
                    {"id": r["id"], "name": r["name"], "done": r["scope"] != "pending"})
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
            return {
                "hidden": False,
                "modules": modules,
                "progress": {"done": done_total, "total": all_total},
                "spotlight": spotlight,
            }

    # ------------------------------------------------- spotlight / client screen
    def get_spotlight(self):
        raw = self.get_meta("spotlight", "")
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
        if item_id:
            row = self._one("SELECT module_id FROM items WHERE id=?", (item_id,))
            if not row:
                raise StoreError("Requirement not found.", 404)
            module_id = row["module_id"]
        elif module_id:
            if not self._one("SELECT 1 FROM modules WHERE id=?", (module_id,)):
                raise StoreError("Module not found.", 404)
        if not module_id:
            self.set_meta("spotlight", "")
            return None
        value = {"module_id": module_id, "item_id": item_id or None}
        self.set_meta("spotlight", json.dumps(value))
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
        mid = _new_id("module-custom")
        with self._tx() as db:
            pos = db.execute("SELECT COALESCE(MAX(position), -1) + 1 AS p FROM modules").fetchone()["p"]
            db.execute("INSERT INTO modules(id,title,description,icon,position,is_custom) VALUES(?,?,?,?,?,1)",
                       (mid, title, description, DEFAULT_ICON, pos))
            row = db.execute("SELECT * FROM modules WHERE id=?", (mid,)).fetchone()
        module = self._module_dict(row)
        module["items"] = []
        return module

    def update_module(self, module_id, title, description):
        title = (title or "").strip()[:200]
        if not title:
            raise StoreError("Please enter a module title.")
        description = (description or "").strip()[:1000] or "Custom business module configuration."
        with self._tx() as db:
            row = db.execute("SELECT * FROM modules WHERE id=?", (module_id,)).fetchone()
            if not row:
                raise StoreError("Module not found.", 404)
            if not row["is_custom"]:
                raise StoreError("Only custom modules can be edited.", 403)
            db.execute("UPDATE modules SET title=?, description=? WHERE id=?", (title, description, module_id))
            row = db.execute("SELECT * FROM modules WHERE id=?", (module_id,)).fetchone()
        return self._module_dict(row)

    def delete_module(self, module_id):
        with self._tx() as db:
            row = db.execute("SELECT * FROM modules WHERE id=?", (module_id,)).fetchone()
            if not row:
                raise StoreError("Module not found.", 404)
            if not row["is_custom"]:
                raise StoreError("Only custom modules can be deleted.", 403)
            db.execute("DELETE FROM modules WHERE id=?", (module_id,))
        sp = self.get_spotlight()
        if sp and sp["module_id"] == module_id:
            self.set_meta("spotlight", "")

    # ------------------------------------------------------------ requirements
    def create_item(self, module_id, name):
        name = (name or "").strip()[:300]
        if not name:
            raise StoreError("Please enter a name.")
        iid = _new_id("custom")
        with self._tx() as db:
            if not db.execute("SELECT 1 FROM modules WHERE id=?", (module_id,)).fetchone():
                raise StoreError("Module not found.", 404)
            pos = db.execute("SELECT COALESCE(MAX(position), -1) + 1 AS p FROM items WHERE module_id=?",
                             (module_id,)).fetchone()["p"]
            db.execute(
                "INSERT INTO items(id,module_id,name,guidance,guidance_edited,scope,priority,criticality,"
                "suppressed,position,is_custom) VALUES(?,?,?,?,0,'pending','phase2','normal',0,?,1)",
                (iid, module_id, name, "Custom focus item added by user.", pos))
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
        with self._tx() as db:
            row = db.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
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
                row = db.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
        return self._item_dict(row)

    def delete_item(self, item_id):
        with self._tx() as db:
            row = db.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
            if not row:
                raise StoreError("Requirement not found.", 404)
            if not row["is_custom"]:
                raise StoreError("Only custom requirements can be deleted.", 403)
            db.execute("DELETE FROM items WHERE id=?", (item_id,))
        sp = self.get_spotlight()
        if sp and sp.get("item_id") == item_id:
            self.set_meta("spotlight", json.dumps({"module_id": sp["module_id"], "item_id": None}))
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
        with self._tx() as db:
            if not db.execute("SELECT 1 FROM items WHERE id=?", (item_id,)).fetchone():
                raise StoreError("Requirement not found.", 404)
            cur = db.execute(
                "INSERT INTO notes(item_id,user_id,author,body,created_at,edited_at) VALUES(?,?,?,?,?,NULL)",
                (item_id, user["id"], user["display_name"], body, time.time()))
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
