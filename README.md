# BFLA Lab: Broken Function Level Authorization

This repository contains a simple teaching server and client designed to demonstrate **Broken Function Level Authorization (BFLA)** vulnerabilities in API security.

## Files Included

* **`app.py`**: An offline HTTP server implementing a vulnerable API endpoints structure (such as user management and administrative deletion) with configurable security modes.


* **`client.py`**: A command-line client utility used to interact with the server, test permissions, and forge headers like `X-Role`.