import tempfile


class FileObj:

    def __init__(self, tmp_file):
        self.tmp_file = tmp_file

    def temporary_file_path(self):
        return self.tmp_file

    name = 'test'


def build_file():
    handle, tmp_file = tempfile.mkstemp()
    handle = open(tmp_file, 'wb')
    handle.write("test".encode("utf8"))
    handle.close()

    return tmp_file, FileObj(tmp_file)
