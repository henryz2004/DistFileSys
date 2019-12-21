import os
import pathlib
import pickle


class DistributedFileManager:

    def __init__(self, partition_file=None):
        """

        :param partition_file:  File path of the file that stores a pickled dictionary; keys are user ids and values
                                is the directory path the user has their files in
        """

        if partition_file is None:
            partition_file = "generated_partition.info"

        try:
            with open(partition_file, "rb") as partition_pickle:
                self.paths = pickle.load(partition_pickle)
        except OSError:
            self.paths = {}

        self.partition_file = partition_file
        self.active = []                        # List of user id's that are currently browsing the DFM
        self.user_count = len(self.paths)       # Used so len(self.paths) doesn't need to be used
        self.root = "server_files/dir/"         # Where all the client directories are located

        # Create server_files director and whatnot if not done already
        pathlib.Path(self.root).mkdir(parents=True, exist_ok=True)

        self.chunk_size = 1015                  # Almost 1 KB

    def add_user(self, uid=None):

        real_uid = self._add_user(uid=uid)

        # Write self.paths to disk
        self.complete_dump()

        return real_uid

    def remove_user(self, uid):

        # Don't remove dictionary entry because that info should persist
        # However, do remove the user from self.active
        try:
            self.active.remove(uid)
            return 0
        except TypeError as e:
            return 1

    def open(self, uid, file_path, delegator, callback=None):
        if uid not in self.active:
            return 1

        try:
            prefix = self.root + self.paths[uid]
            path = prefix + '/'.join(get_path(file_path))
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            with open(prefix + file_path, "rb") as user_file:

                # Read in chunks as to not overwhelm the server
                while True:
                    info = user_file.read(self.chunk_size)
                    delegator(uid, file_path, info)  # Give server data
                    if len(info) < self.chunk_size:
                        break  # Reached end of file
            return 0

        except FileNotFoundError as e:
            if callback:
                callback(e)
            else:
                raise e

    def write(self, uid, file_path, contents, mode, callback=None):

        print("[ FM ] Writing contents to", file_path, "for user", uid)

        try:
            prefix = self.root+self.paths[uid]
            path = prefix+'/'.join(get_path(file_path))
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            with open(prefix+file_path, mode) as user_file:
                user_file.write(contents)
        except Exception as e:
            if callback:
                callback(e)
            else:
                raise e

        print("[ FM ] Finished writing contents")

    def ldir(self, uid, dirpath):

        dirs = next(os.walk(self.root+self.paths[uid]+dirpath))[1]
        files = next(os.walk(self.root+self.paths[uid]+dirpath))[2]

        return dirs, files

    def complete_dump(self):
        """Saves everything that needs to be saved"""

        with open(self.partition_file, "wb") as partition_pickle:
            pickle.dump(self.paths, partition_pickle)

    def _add_user(self, uid=None):

        # No user id means the client hasn't been given a user id yet and return uid
        if uid is None:
            self.paths[self.user_count] = "uid"+str(self.user_count)+"/"
            self.active.append(self.user_count)
            self.user_count += 1
            return self.user_count - 1

        assert type(uid) is int, "Parameter uid should be integer for DFM.add_user(uid=...)"

        self.paths[uid] = "uid"+str(uid)+"/"
        self.active.append(uid)
        self.user_count += 1
        return uid


def get_path(file_path):
    return file_path.split("/")[:-1]


def get_file_name(file_path):
    return file_path.split("/")[-1]