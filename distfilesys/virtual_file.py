class VFile:

    def __init__(self, file_name, binary=True):

        self.file = file_name
        self.binary = binary

        # Store contents of file in variable if file already exists
        try:
            if binary:
                with open(file_name, "rb") as f:
                    self.contents_cache = bytearray(f.read())
            else:
                with open(file_name, "r") as f:
                    self.contents_cache = [f.read()]
        except (FileNotFoundError, OSError):
            self.contents_cache = bytearray() if binary else []     # List to store strings

    def read(self):

        if self.binary:
            return bytes(self.contents_cache)

        else:
            return ''.join(self.contents_cache)

    def write(self, data):

        try:
            if self.binary:
                self.contents_cache = bytearray(data)
            else:
                assert isinstance(data, str), "Provided data type does not match type flag (Type Mismatch)"

                self.contents_cache = [data]

        except TypeError:
            raise TypeError("Provided data type does not match type flag (Type Mismatch)")

    def append(self, data):

        try:
            if self.binary:
                self.contents_cache += data
            else:
                self.contents_cache.append(data)
        except TypeError:
            raise TypeError("Provided data cannot be added to file contents (Type Mismatch)")

    def write_to_disk(self):

        if self.binary:
            print("Writing binary contents_cache to disk")
            with open(self.file, "wb") as f:
                f.write(self.contents_cache)
            print("Finished writing binary contents_cache to disk")
        else:
            print("Writing text contents_cache to disk")
            with open(self.file, "w") as f:
                f.write(''.join(self.contents_cache))
            print("Finished writing text contents_cache to disk")
