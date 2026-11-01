#!/usr/bin/env python3
"""Requirement Gathering web server.

Run it (no third-party packages needed, Python 3.8+):

    python server.py                       # serve on http://0.0.0.0:8000
    python server.py --port 9000
    python server.py adduser alice         # add a team member (prompts for a password)
    python server.py adduser bob --admin   # add another administrator
    python server.py passwd alice          # reset someone's password

Pages
    /         staff app (sign-in required) - capture notes live, together
    /client   client-facing screen - shows topics & progress, never notes

Environment variables / flags: HOST, PORT, DATA_DIR, SEED_FILE, CLIENT_ACCESS_CODE,
ADMIN_PASSWORD (initial password for the auto-created 'admin' account).
"""
import argparse
import getpass
import hmac
import json
import mimetypes
import os
import queue
import re
import secrets
import socket
import sys
import threading
import traceback
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from backend import auth
from backend.events import Hub
from backend.store import Store, StoreError

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ROOT, "web")

# Only these files are ever served. Everything else in the project folder
# (the database, the seed JSON, this script...) is unreachable over HTTP.
STATIC_FILES = {
    "staff.js": os.path.join(WEB, "staff.js"),
    "staff.css": os.path.join(WEB, "staff.css"),
    "client.js": os.path.join(WEB, "client.js"),
    "client.css": os.path.join(WEB, "client.css"),
    "style.css": os.path.join(ROOT, "style.css"),
    "logo.png": os.path.join(ROOT, "WMG-logo.png"),
}
PAGES = {
    "/": os.path.join(WEB, "staff.html"),
    "/staff": os.path.join(WEB, "staff.html"),
    "/client": os.path.join(WEB, "client.html"),
}

SESSION_COOKIE = "sid"
CLIENT_COOKIE = "client_access"
SESSION_TTL = 12 * 3600
MAX_BODY_BYTES = 10 * 1024 * 1024


class HttpError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


class App:
    """Process-wide state shared by every request thread."""

    def __init__(self, store, seed_path, client_code):
        self.store = store
        self.hub = Hub()
        self.limiter = auth.LoginLimiter()
        self.seed_path = seed_path
        self.client_code = client_code or ""
        self.secret = store.secret_key()
        self.stopping = threading.Event()


APP = None  # set in main()

ROUTES = []


def route(method, pattern, access="staff"):
    """access: public | client | staff | admin"""
    def decorator(fn):
        ROUTES.append((method, re.compile("^" + pattern + "$"), fn, access))
        return fn
    return decorator


def _dict(body):
    return body if isinstance(body, dict) else {}


def _broadcast(h, event):
    """Tell every signed-in teammate, then refresh the (sanitised) client screen."""
    event["by"] = h.user["display_name"]
    event["by_id"] = h.user["id"]
    APP.hub.publish_staff(event)
    APP.hub.publish_client_if_changed(APP.store.client_state())


# =============================================================== auth endpoints
@route("POST", "/api/login", "public")
def api_login(h, m, body):
    body = _dict(body)
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))
    key = (h.client_ip, username.lower())
    wait = APP.limiter.retry_after(key)
    if wait:
        raise HttpError(429, "Too many failed attempts. Try again in %d seconds." % wait)
    user, stored = APP.store.get_user_for_login(username)
    valid = auth.verify_password(password, stored or auth.DUMMY_HASH) and user is not None
    if not valid:
        APP.limiter.record_failure(key)
        raise HttpError(401, "Invalid username or password.")
    APP.limiter.clear(key)
    token = APP.store.create_session(user["id"], SESSION_TTL)
    h.set_cookie(SESSION_COOKIE, token, SESSION_TTL)
    return 200, {"user": user}


@route("POST", "/api/logout", "public")
def api_logout(h, m, body):
    APP.store.delete_session(h.get_cookie(SESSION_COOKIE))
    h.set_cookie(SESSION_COOKIE, "", 0)
    return 200, {"ok": True}


@route("GET", "/api/me", "staff")
def api_me(h, m, body):
    return 200, {"user": h.user}


@route("POST", "/api/me/password", "staff")
def api_change_own_password(h, m, body):
    body = _dict(body)
    user, stored = APP.store.get_user_for_login(h.user["username"])
    if not auth.verify_password(str(body.get("current", "")), stored or auth.DUMMY_HASH):
        raise HttpError(403, "Your current password is incorrect.")
    new = str(body.get("new", ""))
    if len(new) < auth.MIN_PASSWORD_LENGTH:
        raise HttpError(400, "New password must be at least %d characters." % auth.MIN_PASSWORD_LENGTH)
    APP.store.set_password_hash(h.user["id"], auth.hash_password(new))
    # set_password_hash signs the user out everywhere; keep *this* browser signed in.
    token = APP.store.create_session(h.user["id"], SESSION_TTL)
    h.set_cookie(SESSION_COOKIE, token, SESSION_TTL)
    return 200, {"ok": True}


@route("GET", "/api/state", "staff")
def api_state(h, m, body):
    state = APP.store.get_state()
    state["user"] = h.user
    state["presence"] = APP.hub.presence()
    return 200, state


@route("GET", "/api/events", "staff")
def api_events(h, m, body):
    sub = APP.hub.subscribe_staff(h.user)
    h.stream(sub, lambda: APP.hub.unsubscribe_staff(sub))


# ======================================================= modules & requirements
@route("POST", "/api/modules")
def api_create_module(h, m, body):
    body = _dict(body)
    module = APP.store.create_module(body.get("title"), body.get("description"))
    _broadcast(h, {"type": "module_added", "module": module})
    return 201, {"module": module}


@route("PATCH", r"/api/modules/([A-Za-z0-9._:-]+)")
def api_update_module(h, m, body):
    body = _dict(body)
    module = APP.store.update_module(m.group(1), body.get("title"), body.get("description"))
    _broadcast(h, {"type": "module_updated", "module": module})
    return 200, {"module": module}


@route("DELETE", r"/api/modules/([A-Za-z0-9._:-]+)")
def api_delete_module(h, m, body):
    APP.store.delete_module(m.group(1))
    _broadcast(h, {"type": "module_deleted", "module_id": m.group(1)})
    return 200, {"ok": True}


@route("POST", r"/api/modules/([A-Za-z0-9._:-]+)/items")
def api_create_item(h, m, body):
    item = APP.store.create_item(m.group(1), _dict(body).get("name"))
    _broadcast(h, {"type": "item_added", "item": item})
    return 201, {"item": item}


@route("PATCH", r"/api/items/([A-Za-z0-9._:-]+)")
def api_update_item(h, m, body):
    item = APP.store.update_item(m.group(1), _dict(body))
    _broadcast(h, {"type": "item_updated", "item": item})
    return 200, {"item": item}


@route("DELETE", r"/api/items/([A-Za-z0-9._:-]+)")
def api_delete_item(h, m, body):
    item = APP.store.delete_item(m.group(1))
    _broadcast(h, {"type": "item_deleted", "item_id": item["id"], "module_id": item["module_id"]})
    return 200, {"ok": True}


# ------------------------------------------------------------------------ notes
@route("POST", r"/api/items/([A-Za-z0-9._:-]+)/notes")
def api_add_note(h, m, body):
    note = APP.store.add_note(m.group(1), h.user, _dict(body).get("body"))
    _broadcast(h, {"type": "note_added", "note": note})
    return 201, {"note": note}


@route("PATCH", r"/api/notes/(\d+)")
def api_edit_note(h, m, body):
    note = APP.store.edit_note(int(m.group(1)), h.user, _dict(body).get("body"))
    _broadcast(h, {"type": "note_updated", "note": note})
    return 200, {"note": note}


@route("DELETE", r"/api/notes/(\d+)")
def api_delete_note(h, m, body):
    note = APP.store.delete_note(int(m.group(1)), h.user)
    _broadcast(h, {"type": "note_deleted", "note_id": note["id"], "item_id": note["item_id"]})
    return 200, {"ok": True}


# ------------------------------------------------------- client screen controls
@route("PUT", "/api/spotlight")
def api_set_spotlight(h, m, body):
    body = _dict(body)
    sp = APP.store.set_spotlight(body.get("module_id") or None, body.get("item_id") or None)
    _broadcast(h, {"type": "spotlight", "spotlight": sp})
    return 200, {"spotlight": sp}


@route("PUT", "/api/client-screen")
def api_set_client_screen(h, m, body):
    hidden = APP.store.set_client_hidden(bool(_dict(body).get("hidden")))
    _broadcast(h, {"type": "client_screen", "hidden": hidden})
    return 200, {"hidden": hidden}


# ------------------------------------------------------------ admin: data & team
@route("POST", "/api/import", "admin")
def api_import(h, m, body):
    raw = body.get("modules") if isinstance(body, dict) else body
    modules, items = APP.store.import_modules(raw)
    _broadcast(h, {"type": "reload"})
    return 200, {"modules": modules, "items": items}


@route("POST", "/api/reset", "admin")
def api_reset(h, m, body):
    APP.store.reset_to_seed(APP.seed_path)
    _broadcast(h, {"type": "reload"})
    return 200, {"ok": True}


@route("GET", "/api/users", "admin")
def api_list_users(h, m, body):
    return 200, {"users": APP.store.list_users()}


@route("POST", "/api/users", "admin")
def api_create_user(h, m, body):
    body = _dict(body)
    password = str(body.get("password", ""))
    if len(password) < auth.MIN_PASSWORD_LENGTH:
        raise HttpError(400, "Password must be at least %d characters." % auth.MIN_PASSWORD_LENGTH)
    user = APP.store.create_user(body.get("username"), auth.hash_password(password),
                                 body.get("display_name"), body.get("role") or "staff")
    return 201, {"user": user}


@route("DELETE", r"/api/users/(\d+)", "admin")
def api_delete_user(h, m, body):
    user_id = int(m.group(1))
    if user_id == h.user["id"]:
        raise HttpError(409, "You can't remove your own account.")
    APP.store.delete_user(user_id)
    return 200, {"ok": True}


@route("POST", r"/api/users/(\d+)/password", "admin")
def api_reset_user_password(h, m, body):
    password = str(_dict(body).get("password", ""))
    if len(password) < auth.MIN_PASSWORD_LENGTH:
        raise HttpError(400, "Password must be at least %d characters." % auth.MIN_PASSWORD_LENGTH)
    APP.store.set_password_hash(int(m.group(1)), auth.hash_password(password))
    return 200, {"ok": True}


# ============================================================= client-screen API
@route("GET", "/api/client/config", "public")
def api_client_config(h, m, body):
    needs = bool(APP.client_code)
    authed = (not needs) or h.user is not None or h.client_cookie_ok()
    return 200, {"requires_code": needs, "authed": authed}


@route("POST", "/api/client/login", "public")
def api_client_login(h, m, body):
    if not APP.client_code:
        return 200, {"ok": True}
    key = (h.client_ip, "<client-code>")
    wait = APP.limiter.retry_after(key)
    if wait:
        raise HttpError(429, "Too many attempts. Try again in %d seconds." % wait)
    supplied = str(_dict(body).get("code", ""))
    if not hmac.compare_digest(supplied.encode("utf-8"), APP.client_code.encode("utf-8")):
        APP.limiter.record_failure(key)
        raise HttpError(401, "That access code isn't right.")
    APP.limiter.clear(key)
    h.set_cookie(CLIENT_COOKIE, auth.client_cookie_value(APP.secret), SESSION_TTL)
    return 200, {"ok": True}


@route("GET", "/api/client/state", "client")
def api_client_state(h, m, body):
    return 200, APP.store.client_state()


@route("GET", "/api/client/events", "client")
def api_client_events(h, m, body):
    sub = APP.hub.subscribe_client()
    sub.offer({"type": "state", "state": APP.store.client_state()})
    h.stream(sub, lambda: APP.hub.unsubscribe_client(sub))


# ================================================================ HTTP plumbing
class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"  # one request per connection keeps SSE simple
    server_version = "ReqGather/1.0"
    sys_version = ""

    # ---- logging: stay quiet for routine GETs, show writes and errors -------
    def log_message(self, fmt, *args):
        pass

    def log_request(self, code="-", size="-"):
        try:
            status = int(code)
        except (TypeError, ValueError):
            status = 0
        if self.command != "GET" or status >= 400:
            sys.stderr.write("%s %s %s -> %s\n" % (self.client_ip, self.command, self.path, code))

    @property
    def client_ip(self):
        return self.client_address[0] if self.client_address else "?"

    # ---- verbs ---------------------------------------------------------------
    def do_GET(self):
        self._dispatch("GET")

    def do_POST(self):
        self._dispatch("POST")

    def do_PUT(self):
        self._dispatch("PUT")

    def do_PATCH(self):
        self._dispatch("PATCH")

    def do_DELETE(self):
        self._dispatch("DELETE")

    # ---- cookies -------------------------------------------------------------
    def get_cookie(self, name):
        try:
            jar = cookies.SimpleCookie(self.headers.get("Cookie", ""))
        except cookies.CookieError:
            return None
        return jar[name].value if name in jar else None

    def set_cookie(self, name, value, max_age):
        self.extra_headers.append(
            ("Set-Cookie", "%s=%s; Path=/; HttpOnly; SameSite=Lax; Max-Age=%d" % (name, value, max_age)))

    def client_cookie_ok(self):
        return auth.check_client_cookie(APP.secret, self.get_cookie(CLIENT_COOKIE))

    # ---- dispatch -----------------------------------------------------------
    def _dispatch(self, method):
        self.extra_headers = []
        self.user = None
        path = urlparse(self.path).path
        try:
            if method == "GET" and not path.startswith("/api/"):
                return self._serve_static(path)

            if method != "GET":
                origin = self.headers.get("Origin")
                if origin and urlparse(origin).netloc != self.headers.get("Host", ""):
                    raise HttpError(403, "Cross-site request blocked.")

            for verb, pattern, fn, access in ROUTES:
                if verb != method:
                    continue
                match = pattern.match(path)
                if not match:
                    continue
                self.user = APP.store.user_for_session(self.get_cookie(SESSION_COOKIE))
                if access in ("staff", "admin"):
                    if not self.user:
                        raise HttpError(401, "Please sign in.")
                    if access == "admin" and self.user["role"] != "admin":
                        raise HttpError(403, "Administrator access required.")
                elif access == "client":
                    if APP.client_code and not (self.user or self.client_cookie_ok()):
                        raise HttpError(401, "Access code required.")
                body = self._read_json() if method in ("POST", "PUT", "PATCH") else None
                result = fn(self, match, body)
                if result is not None:
                    self._send_json(*result)
                return
            raise HttpError(404, "Not found.")
        except HttpError as err:
            self._send_json(err.status, {"error": err.message})
        except StoreError as err:
            self._send_json(err.status, {"error": err.message})
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass
        except Exception:
            traceback.print_exc()
            try:
                self._send_json(500, {"error": "Something went wrong on the server."})
            except OSError:
                pass

    def _read_json(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            raise HttpError(400, "Bad Content-Length.")
        if length <= 0:
            return {}
        if length > MAX_BODY_BYTES:
            raise HttpError(413, "That request is too large.")
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            raise HttpError(400, "Request body must be valid JSON.")

    # ---- responses -----------------------------------------------------------
    def _security_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Referrer-Policy", "no-referrer")

    def _send_json(self, status, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self._security_headers()
        for key, value in self.extra_headers:
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def _serve_static(self, path):
        if path in PAGES:
            fs_path = PAGES[path]
        elif path.startswith("/static/") and path[len("/static/"):] in STATIC_FILES:
            fs_path = STATIC_FILES[path[len("/static/"):]]
        else:
            raise HttpError(404, "Not found.")
        try:
            with open(fs_path, "rb") as fh:
                data = fh.read()
        except OSError:
            raise HttpError(404, "Not found.")
        ctype = mimetypes.guess_type(fs_path)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript", "text/javascript"):
            ctype += "; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self._security_headers()
        self.end_headers()
        self.wfile.write(data)

    def stream(self, sub, cleanup):
        """Hold the connection open and pump events to the browser (SSE)."""
        self.close_connection = True
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-transform")
        self.send_header("X-Accel-Buffering", "no")
        self._security_headers()
        self.end_headers()
        try:
            self.wfile.write(b"retry: 3000\n\n")
            self.wfile.flush()
            while not APP.stopping.is_set():
                try:
                    message = sub.queue.get(timeout=15)
                except queue.Empty:
                    self.wfile.write(b": ping\n\n")  # keeps proxies happy & detects dead peers
                    self.wfile.flush()
                    continue
                payload = json.dumps(message, separators=(",", ":"))
                self.wfile.write(("data: %s\n\n" % payload).encode("utf-8"))
                self.wfile.flush()
        except OSError:
            pass  # browser went away
        finally:
            cleanup()


class Server(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 64


# ===================================================================== CLI
def _lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return None


def _prompt_password(label):
    while True:
        first = getpass.getpass("Password for %s (min %d chars): " % (label, auth.MIN_PASSWORD_LENGTH))
        if len(first) < auth.MIN_PASSWORD_LENGTH:
            print("Too short.")
            continue
        if first != getpass.getpass("Repeat password: "):
            print("Passwords didn't match.")
            continue
        return first


def _bootstrap_admin(store):
    if store.user_count():
        return
    password = os.environ.get("ADMIN_PASSWORD") or secrets.token_urlsafe(9)
    store.create_user("admin", auth.hash_password(password), "Administrator", "admin")
    bar = "=" * 62
    print(bar)
    print(" First run: created the administrator account")
    print("     username: admin")
    print("     password: %s" % password)
    print(" Sign in, then add your team under  Team  in the sidebar,")
    print(" and change this password.")
    print(bar)


def main(argv=None):
    global APP
    parser = argparse.ArgumentParser(description="Requirement Gathering web server")
    parser.add_argument("command", nargs="?", default="serve", choices=("serve", "adduser", "passwd"))
    parser.add_argument("username", nargs="?")
    parser.add_argument("--host", default=os.environ.get("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))
    parser.add_argument("--data-dir", default=os.environ.get("DATA_DIR", os.path.join(ROOT, "data")))
    parser.add_argument("--seed", default=os.environ.get("SEED_FILE", os.path.join(ROOT, "ReqGather_Backup_Config.json")))
    parser.add_argument("--client-code", default=os.environ.get("CLIENT_ACCESS_CODE", ""),
                        help="optional access code the client screen asks for")
    parser.add_argument("--admin", action="store_true", help="adduser: make the new user an administrator")
    args = parser.parse_args(argv)

    os.makedirs(args.data_dir, exist_ok=True)
    gitignore = os.path.join(args.data_dir, ".gitignore")
    if not os.path.exists(gitignore):
        with open(gitignore, "w") as fh:  # never commit the database or password hashes
            fh.write("*\n")
    store = Store(os.path.join(args.data_dir, "reqgather.db"))

    if args.command in ("adduser", "passwd"):
        if not args.username:
            parser.error("%s needs a username" % args.command)
        if args.command == "adduser":
            user = store.create_user(args.username, auth.hash_password(_prompt_password(args.username)),
                                     args.username, "admin" if args.admin else "staff")
            print("Created %s '%s'." % (user["role"], user["username"]))
        else:
            user, _ = store.get_user_for_login(args.username)
            if not user:
                sys.exit("No such user: %s" % args.username)
            store.set_password_hash(user["id"], auth.hash_password(_prompt_password(args.username)))
            print("Password updated for '%s'." % user["username"])
        return

    seed_status = store.ensure_seeded(args.seed)
    _bootstrap_admin(store)
    APP = App(store, args.seed, args.client_code)

    server = Server((args.host, args.port), Handler)
    lan = _lan_ip()
    print("Requirement Gathering server (%s)" % seed_status)
    print("  Staff app      http://localhost:%d/" % args.port)
    print("  Client screen  http://localhost:%d/client%s" % (
        args.port, "   (access code required)" if args.client_code else ""))
    if lan and args.host in ("0.0.0.0", ""):
        print("  On your network: http://%s:%d/   and   http://%s:%d/client" % (lan, args.port, lan, args.port))
    print("  Data stored in %s   -   Ctrl+C to stop" % os.path.abspath(args.data_dir))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        APP.stopping.set()
        server.server_close()


if __name__ == "__main__":
    main()
