import os
import shutil
import urllib
import urllib2
from HTMLParser import HTMLParser

# IP address of your Windows 7 VM
SERVER_URL = "http://192.168.37.16"
LOCAL_TESTS_DIR = r"C:\tests"


class SimpleDirectoryParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr, value in attrs:
                if attr == "href":
                    self.links.append(value)


def download_folder(remote_folder_name, relative_path=""):
    """Recursively downloads a directory tree over HTTP in Python 2.7."""
    remote_url = (
        SERVER_URL
        + "/"
        + relative_path
        + urllib.quote(remote_folder_name)
        + "/"
    )
    local_target = os.path.join(
        LOCAL_TESTS_DIR, relative_path.replace("/", os.sep)
    )

    if not os.path.exists(local_target):
        os.makedirs(local_target)

    req = urllib2.urlopen(remote_url)
    html_content = req.read().decode("utf-8")

    parser = SimpleDirectoryParser()
    parser.feed(html_content)

    for link in parser.links:
        if link in ["../", "./", "/"]:
            continue

        decoded = urllib.unquote(link)

        if link.endswith("/"):
            # Recurse into subfolder
            subfolder_name = decoded.rstrip("/")
            next_relative = (
                relative_path + urllib.quote(remote_folder_name) + "/"
            )
            download_folder(subfolder_name, next_relative)
        else:
            # Download file
            file_url = remote_url + urllib.quote(decoded)
            local_file_path = os.path.join(local_target, decoded)
            print "Downloading: " + decoded
            urllib.urlretrieve(file_url, local_file_path)


def fetch_and_claim_latest_test():
    """Finds the first folder on the Win7 server, downloads it, and deletes remote copy."""
    try:
        req = urllib2.urlopen(SERVER_URL)
        html_content = req.read().decode("utf-8")
    except Exception as e:
        print "Failed to connect to Win7 server: " + str(e)
        return False

    parser = SimpleDirectoryParser()
    parser.feed(html_content)

    # Filter out directory links to isolate target folder names
    folders = [
        urllib.unquote(l.rstrip("/"))
        for l in parser.links
        if l.endswith("/") and l not in ["../", "./", "/"]
    ]

    if not folders:
        print "No test packages available on server."
        return False

    target_folder = folders[0]
    print "Downloading test suite: " + target_folder

    # Clean destination directory before extraction
    if os.path.exists(LOCAL_TESTS_DIR):
        shutil.rmtree(LOCAL_TESTS_DIR)

    download_folder(target_folder)

    # Send POST request to Win7 server to delete the folder
    print "Requesting remote deletion of: " + target_folder
    delete_url = SERVER_URL + "/delete"
    post_data = target_folder.encode("utf-8")

    req = urllib2.Request(delete_url, data=post_data)
    try:
        response = urllib2.urlopen(req)
        if response.getcode() == 200:
            print "Server deleted remote copy successfully."
    except Exception as e:
        print "Failed to delete remote folder: " + str(e)

    return True


if __name__ == "__main__":
    fetch_and_claim_latest_test()
