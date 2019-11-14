#!/usr/bin/env python3

import os
try:
    # Posix based file locking for Linux and MacOS
    import fcntl
    ON_LINUX = True
except ModuleNotFoundError:
    # Windows file locking
    import msvcrt
    ON_LINUX = False


CORIOLIS_LOGGER_OUTPUT_FILE = "/logs/coriolis_run.log"

class CoriolisLogger:
    def __init__(self):
        self.fd = open(CORIOLIS_LOGGER_OUTPUT_FILE, "a+")
        self._lock_file()

    def _flush_file(self):
        # Flush to make sure all buffered contents are written to file.
        self.fd.flush()
        os.fsync(self.fd.fileno())


    def write(self, log_line):
        self._flush_file()
        self.fd.write("{}\n".format(log_line))
        self._flush_file()

    def __exit__(self):
        self._unlock_file()
        self.fd.close()

    if ON_LINUX:
        def _lock_file(self):
            fcntl.lockf(self.fd, fcntl.LOCK_EX)

        def _unlock_file(self):
            fcntl.lockf(self.fd, fcntl.LOCK_UN)

    else:
        def _file_size(self):
            return os.path.getsize( os.path.realpath(self.fd.name) )

        def _lock_file(self):
            msvcrt.locking(self.fd.fileno(), msvcrt.LK_RLCK, self._file_size())

        def _unlock_file(self):
            msvcrt.locking(self.fd.fileno(), msvcrt.LK_UNLCK, self._file_size())


def coriolis_logger_write(log_line):
    cl = CoriolisLogger()
    cl.write(log_line)