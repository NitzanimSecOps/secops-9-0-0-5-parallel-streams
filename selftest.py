"""Local tester for server.py and client.py - not the hidden grader.

    python3 selftest.py

Creates a large file in files/, starts your server.py in the background, downloads it with your
start_download, and runs a command during the download. Change the examples and try your own.
"""
import os
import socket
import subprocess
import sys
import time

HOST = "127.0.0.1"
PORT = 2405


def port_is_taken():
    try:
        socket.create_connection((HOST, PORT), timeout=1).close()
        return True
    except OSError:
        return False


def main():
    if port_is_taken():
        print(f"Something (probably a server.py you started) is already listening on port {PORT}.")
        print("Stop it with Ctrl+C in its window, then run selftest.py again.")
        sys.exit(1)
    here = os.path.dirname(os.path.abspath(__file__))
    files = os.path.join(here, "files")
    os.makedirs(files, exist_ok=True)
    with open(os.path.join(files, "big.bin"), "wb") as f:
        f.write(os.urandom(1024 * 1024) * 30)

    dest = os.path.join(here, "downloaded_big.bin")
    server = subprocess.Popen([sys.executable, os.path.join(here, "server.py")], cwd=here)
    try:
        time.sleep(1)
        if server.poll() is not None:
            print("server.py stopped right after starting (its error is printed above).")
            sys.exit(1)
        sys.path.insert(0, here)
        from client import run_command, start_download

        with socket.create_connection((HOST, PORT)) as s:
            s.settimeout(10)
            transfer = start_download(s, HOST, PORT, "big.bin", dest)
            print("started:", transfer)
            print("command during the download:", run_command(s, "echo hello")["stdout"].strip())
            print("progress:", transfer["received"], "of", transfer["size"])
            while not transfer["done"]:
                time.sleep(0.1)
            print("finished:", transfer)
            print("missing file:", start_download(s, HOST, PORT, "nope.bin", dest + ".nope"))
    finally:
        server.kill()
        os.remove(os.path.join(files, "big.bin"))
        if os.path.exists(dest):
            os.remove(dest)


if __name__ == "__main__":
    main()
