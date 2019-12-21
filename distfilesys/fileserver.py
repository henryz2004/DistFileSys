from pynet import serverbackend_rewrite
from virtual_file import VFile
import os


def write(server, client_socket, client_ip, filename, data, mode):
    global active_files

    if filename in active_files:
        v_file = active_files[filename]
    else:
        v_file = VFile(filename, "b" in mode)
        active_files[filename] = v_file

    print("Writing")
    if mode[0] == "w":
        v_file.write(data)
    elif mode[0] == "a":
        v_file.append(data)
    print("Written")


def read(server, client_socket, client_ip, filename, binary):
    global active_files

    print("Reading")

    if not os.path.isfile(filename):
        return None

    if filename not in active_files:
        active_files[filename] = VFile(filename, binary)

    v_file = active_files[filename]
    if binary != v_file.binary:
        return False                # Will definitely need ability to throw exception

    print("Returning file read data")

    return v_file.read()


def on_shutdown(*_):
    print("Server shutting down,", len(active_files), "files active")
    for filename, v_file in active_files.items():
        v_file.write_to_disk()
    print("Contents dumped to disk")


if __name__ == "__main__":

    active_files = {}

    serverbackend_rewrite.Server(
        31415,
        events={
            "write": write
        },
        functions={
            "read": read
        },
        on_shutdown=on_shutdown
    ).start(5, False)
