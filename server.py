import http.server
import os
import shutil
import socketserver
import urllib.parse

ARTIFACTS_DIR = r"C:\Tests_For_Carrier-Win2003-x64"
PORT = 8000


class ArtifactHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ARTIFACTS_DIR, **kwargs)

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)

        if parsed_path.path == "/delete":
            content_length = int(self.headers.get("Content-Length", 0))
            folder_name = self.rfile.read(content_length).decode("utf-8").strip()

            safe_folder_name = os.path.basename(folder_name)
            target_path = os.path.join(ARTIFACTS_DIR, safe_folder_name)

            if os.path.exists(target_path) and os.path.isdir(target_path):
                try:
                    shutil.rmtree(target_path)
                    print(
                        f"[SERVER] Successfully deleted folder: {safe_folder_name}"
                    )
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"Deleted successfully")
                except Exception as e:
                    print(
                        f"[SERVER] Error deleting {safe_folder_name}: {str(e)}"
                    )
                    self.send_error(500, f"Delete failed: {str(e)}")
            else:
                self.send_error(404, "Folder not found")
        else:
            self.send_error(404, "Unknown endpoint")


def run_server():
    os.chdir(ARTIFACTS_DIR)
    with socketserver.TCPServer(("", PORT), ArtifactHandler) as httpd:
        print(f"[SERVER] Serving {ARTIFACTS_DIR} on port {PORT}...")
        httpd.serve_forever()


if __name__ == "__main__":
    run_server()
