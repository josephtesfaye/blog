#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os
import sys

# Directory you want to expose
ROOT = Path(os.path.expanduser("~/Downloads/temp/archive/image/foo")).resolve()

MOUNT = "/igps/"
HOST = "127.0.0.1"
PORT = 8123


class MountHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        """
        Map URLs under /igps/... to files under ROOT/...
        Reject everything else with a 404.
        """
        # Strip query/fragment
        path = path.split("?", 1)[0].split("#", 1)[0]

        if not path.startswith(MOUNT):
            # Send 404 for non-mounted paths
            return str(ROOT / "__nonexistent__")

        rel = path[len(MOUNT):]  # e.g. "20260218184820.png"
        # Normalize and prevent path traversal
        rel_path = Path(rel)
        full = (ROOT / rel_path).resolve()

        if ROOT not in full.parents and full != ROOT:
            return str(ROOT / "__nonexistent__")

        return str(full)

    def log_message(self, fmt, *args):
        # optional: quieter logs
        sys.stderr.write("%s - - [%s] %s\n" % (self.client_address[0],
                                              self.log_date_time_string(),
                                              fmt % args))


if __name__ == "__main__":
    if not ROOT.exists():
        print(f"ERROR: directory does not exist: {ROOT}", file=sys.stderr)
        sys.exit(1)

    httpd = ThreadingHTTPServer((HOST, PORT), MountHandler)
    print(f"Serving {ROOT} at http://{HOST}:{PORT}{MOUNT}")
    httpd.serve_forever()
