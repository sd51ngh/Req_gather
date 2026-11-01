"""Password hashing, login throttling and the optional client access code."""
import hashlib
import hmac
import secrets
import threading
import time

_ITERATIONS = 240000
MIN_PASSWORD_LENGTH = 8


def hash_password(password, iterations=_ITERATIONS):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), iterations)
    return "pbkdf2_sha256$%d$%s$%s" % (iterations, salt, digest.hex())


def verify_password(password, stored):
    try:
        scheme, iterations, salt, expected = stored.split("$")
        if scheme != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), int(iterations))
        return hmac.compare_digest(digest.hex(), expected)
    except (ValueError, AttributeError):
        return False


# Used to burn the same CPU time when a username doesn't exist, so response
# timing doesn't reveal which usernames are valid.
DUMMY_HASH = hash_password("not-a-real-password")


class LoginLimiter:
    """Locks an (ip, username) pair for a while after repeated failures."""

    def __init__(self, max_failures=6, window_seconds=300):
        self._max = max_failures
        self._window = window_seconds
        self._failures = {}
        self._lock = threading.Lock()

    def _recent(self, key, now):
        recent = [t for t in self._failures.get(key, []) if now - t < self._window]
        if recent:
            self._failures[key] = recent
        else:
            self._failures.pop(key, None)
        return recent

    def retry_after(self, key):
        """Seconds the caller must wait, or 0 if the attempt is allowed."""
        now = time.time()
        with self._lock:
            recent = self._recent(key, now)
            if len(recent) >= self._max:
                return int(self._window - (now - recent[0])) + 1
        return 0

    def record_failure(self, key):
        with self._lock:
            self._failures.setdefault(key, []).append(time.time())

    def clear(self, key):
        with self._lock:
            self._failures.pop(key, None)


def client_cookie_value(secret_key):
    return hmac.new(secret_key.encode("utf-8"), b"client-screen-access", hashlib.sha256).hexdigest()


def check_client_cookie(secret_key, value):
    return bool(value) and hmac.compare_digest(client_cookie_value(secret_key), value)
