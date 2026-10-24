"""Offline BFLA teaching server. Run only in the supplied sandbox."""

import argparse
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

        if self.server.secure:
            # Authorize both admin functions using the server-held role.
            if user["role"] != "admin":
                self.reply(403, {"error": "Admin role required"})
                return
        elif delete_user:
            # VULNERABLE: The caller can forge this role header.
            if self.headers.get("X-Role") != "admin":
                self.reply(403, {"error": "Admin role required"})
                return
        
        # VULNERABLE: Listing users has no role check in the default mode.
        if list_users:
            self.reply(200, {"users": list(USERS.values())})
        elif USERS.pop(42, None) is None:
            self.reply(404, {"error": "User not found"})
        else:
            self.reply(200, {"deleted_user_id": 42})

    do_GET = handle_request
    do_DELETE = handle_request


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--secure", action="store_true")
    args = parser.parse_args()
    # Loopback only; restarting restores all fictional users.
    server = HTTPServer(("127.0.0.1", 5000), API)
    server.secure = args.secure
    print(f"{'Secure' if args.secure else 'Vulnerable'} API: http://127.0.0.1:5000", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
