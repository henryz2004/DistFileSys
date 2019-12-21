from pynet import clientbackend_rewrite
from pynet import updated_call_rf


def write(file_path, data, binary=False):
    """Invokes a series of remote events so that data is sent in chunks as to not overflow recv(bytes)"""

    data_size = len(data)
    chunk_size = 5096
    start_index = 5096

    client.fire_event("write", file_path, data[:start_index], "w" if not binary else "wb")

    while start_index < data_size:
        chunk = data[start_index:start_index+chunk_size]
        client.fire_event("write", file_path, chunk, "a" if not binary else "ab")
        start_index += chunk_size


def read(file_path, binary=False):
    return updated_call_rf(client, "read", file_path, binary)


if __name__ == "__main__":

    client = clientbackend_rewrite.Client(31415)
    thread = client.start(True)

    thread.start()

    with open(r"C:\Users\henry\OneDrive\Pictures\hbdiz.png", "rb") as image_file:
        write("hbdiz.png", image_file.read(), binary=True)

    file_data = read("virtual_file.py")
    print(file_data)

    print("Done")

    client.shutdown_server()
