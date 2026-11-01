"""In-process publish/subscribe hub that feeds Server-Sent-Event streams.

Two audiences:
  * staff   - signed-in team members; receive granular change events
  * clients - the public client screen; only ever receive sanitised snapshots,
              and only when that sanitised snapshot actually changed
              (so e.g. adding a note produces *no* traffic to the client screen).
"""
import json
import queue
import threading


class Subscriber:
    def __init__(self, user=None):
        self.queue = queue.Queue(maxsize=500)
        self.user = user  # None for client-screen subscribers

    def offer(self, message):
        try:
            self.queue.put_nowait(message)
        except queue.Full:
            # Slow consumer: drop the backlog and tell it to resync from scratch.
            try:
                while True:
                    self.queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self.queue.put_nowait({"type": "reload"})
            except queue.Full:
                pass


class Hub:
    def __init__(self):
        self._lock = threading.Lock()
        self._staff = set()
        self._clients = set()
        self._last_client_digest = None

    # ------------------------------------------------------------------ staff
    def subscribe_staff(self, user):
        sub = Subscriber(user)
        with self._lock:
            self._staff.add(sub)
        self.publish_presence()
        return sub

    def unsubscribe_staff(self, sub):
        with self._lock:
            self._staff.discard(sub)
        self.publish_presence()

    def presence(self):
        """Distinct signed-in users that currently have the app open."""
        with self._lock:
            seen, users = set(), []
            for sub in self._staff:
                if sub.user["id"] not in seen:
                    seen.add(sub.user["id"])
                    users.append({"id": sub.user["id"], "name": sub.user["display_name"]})
        users.sort(key=lambda u: u["name"].lower())
        return users

    def publish_staff(self, event):
        with self._lock:
            targets = list(self._staff)
        for sub in targets:
            sub.offer(event)

    def publish_presence(self):
        self.publish_staff({"type": "presence", "users": self.presence()})

    # ---------------------------------------------------------------- clients
    def subscribe_client(self):
        sub = Subscriber()
        with self._lock:
            self._clients.add(sub)
        return sub

    def unsubscribe_client(self, sub):
        with self._lock:
            self._clients.discard(sub)

    def publish_client_if_changed(self, state):
        digest = json.dumps(state, sort_keys=True)
        with self._lock:
            if digest == self._last_client_digest:
                return
            self._last_client_digest = digest
            targets = list(self._clients)
        for sub in targets:
            sub.offer({"type": "state", "state": state})
