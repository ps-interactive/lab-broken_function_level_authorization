"""Offline BFLA teaching server - Remediated version."""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit

# Fixed tokens represent already-authenticated lab sessions, not real credentials.
SESSIONS = {
    "alice-token": {"id": 7, "name": "Alice", "role": "user"},
    "admin-token": {"id": 1, "name": "Admin", "role": "admin"},
}
USERS = {
    1: {"id": 1, "name": "Admin", "role": "admin"},
    7: {"id": 7, "name": "Alice", "role": "user"},
    42: {"id": 42, "name": "Bob", "role": "user"},
}


class API(BaseHTTPRequestHandler):
    def reply(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def handle_request(self):
        path = urlsplit(self.path).path
        user = SESSIONS.get(self.headers.get("Authorization", "").removeprefix("Bearer "))
        if user is None:
            self.reply(401, {"error": "Authentication required"})
            return

        if path == "/api/v1/me" and self.command == "GET":
            self.reply(200, user)
            return

        if path == "/api/v1/ui" and self.command == "GET":
            # Hiding controls does not authorize API requests.
            controls = ["profile"]
            if user["role"] == "admin":
                controls += ["list_users", "delete_user"]
            self.reply(200, {"visible_controls": controls})
            return

        list_users = path == "/api/v1/users" and self.command == "GET"
        delete_user = path == "/api/v1/admin/users/42" and self.command == "DELETE"
        if not (list_users or delete_user):
            self.reply(404, {"error": "Route not found"})
            return

        # SECURE: Enforce strict server-side RBAC for all administrative functions
        if user["role"] != "admin":
            self.reply(403, {"error": "Admin role required"})
            return

        if list_users:
            self.reply(200, {"users": list(USERS.values())})
        elif USERS.pop(42, None) is None:
            self.reply(404, {"error": "User not found"})
        else:
            self.reply(200, {"deleted_user_id": 42})

    do_GET = handle_request
    do_DELETE = handle_request


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 5000), API)
    print("Secure API server running at: http://127.0.0.1:5000", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()