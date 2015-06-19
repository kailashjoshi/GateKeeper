__author__ = 'Kailash Joshi'

import select
from select import kqueue, kevent
import os
import logging
import sys

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)d %(levelname)s %(process)s %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S")

_OS_OPEN_FLAGS = os.O_RDONLY | os.O_NONBLOCK
_FILTER = select.KQ_FILTER_VNODE
_FLAGS = select.KQ_EV_ADD | select.KQ_EV_ENABLE | select.KQ_EV_CLEAR
_FFLAGS = (select.KQ_NOTE_DELETE |
           select.KQ_NOTE_WRITE |
           select.KQ_NOTE_EXTEND |
           select.KQ_NOTE_ATTRIB |
           select.KQ_NOTE_LINK |
           select.KQ_NOTE_RENAME |
           select.KQ_NOTE_REVOKE)

'''
This class watches only directory created/deleted in the top folder

'''


class FileWatcher(object):
    def __init__(self, dir_path):
        try:
            self._file_path = dir_path
            self._snapshot = next(os.walk(dir_path))[1]

            self._file_descriptor = os.open(dir_path, _OS_OPEN_FLAGS)
            self._event = kevent(self._file_descriptor, filter=_FILTER,
                                 flags=_FLAGS,
                                 fflags=_FFLAGS)
            self._kq = kqueue()
            self._kq.control([self._event], 10000000, 0)
        except OSError, e:
            logging.error(e)
        except Exception, e:
            logging.error(e)

    def run(self):
        try:
            while True:
                fetch_events = self._kq.control(None, 1)

                for event in fetch_events:
                    fflag = event.fflags
                    etyp = select.KQ_NOTE_WRITE
                    if fflag == 18 and etyp == 2:
                        self.is_add_delete()
        except KeyboardInterrupt:
            pass
        except Exception, e:
            logging.error(e)

    def is_add_delete(self):
        new_snapshot = self._get_snapshot()
        len_diff = len(self._snapshot) - len(new_snapshot)
        if len_diff > 0:
            diff = list(set(self._snapshot) - set(new_snapshot))
            self._snapshot = new_snapshot
            for d in diff:
                logging.info("Directory '{0}' is deleted".format(os.path.join(self._file_path, d)))
        else:
            diff = list(set(new_snapshot) - set(self._snapshot))
            self._snapshot = new_snapshot
            for d in diff:
                logging.info("New directory '{0}' is created".format(os.path.join(self._file_path, d)))

    def _get_snapshot(self):
        return next(os.walk(self._file_path))[1]

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.close(self._file_descriptor)
        self._kq.close()
        print 'Good Bye'


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath('.')
    f = FileWatcher(path)
    with f:
        f.run()
