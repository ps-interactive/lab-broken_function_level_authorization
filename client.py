"""Small local API client: change the method, path, and optional role header."""

import argparse
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

parser = argparse.ArgumentParser()
parser.add_argument("method", choices=["GET", "DELETE"])
parser.add_argument("path", choices=["/api/v1/me", "/api/v1/ui", "/api/v1/users", "/api/v1/admin/users/42"])
parser.add_argument("--token", default="alice-token")
parser.add_argument("--role")
args = parser.parse_args()

# Keep Alice's identity while manipulating the request.
headers = {"Authorization": f"Bearer {args.token}"}
if args.role:
    headers["X-Role"] = args.role
request = Request("http://127.0.0.1:5000" + args.path, headers=headers, method=args.method)

# Ignore environment proxies: all traffic stays on loopback.
client = build_opener(ProxyHandler({}))
try:
    response = client.open(request, timeout=5)
except HTTPError as error:
    response = error  # Show rejected requests as well as successful ones.
with response:
    print(f"HTTP {response.status}")
    print(response.read().decode())
