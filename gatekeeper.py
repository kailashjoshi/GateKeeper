__author__ = 'Kailash Joshi'

import select
from select import kqueue, kevent
import os
import logging
from dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff
from message import Message
import sys
import time

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)d %(levelname)s %(process)s %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S")

DIR_OPEN_TYPE = os.O_RDONLY | os.O_NONBLOCK
FILTER = select.KQ_FILTER_VNODE
FLAGS = select.KQ_EV_ADD | select.KQ_EV_ENABLE | select.KQ_EV_CLEAR
FFLAGS = (select.KQ_NOTE_DELETE |
          select.KQ_NOTE_WRITE |
          select.KQ_NOTE_EXTEND |
          select.KQ_NOTE_ATTRIB |
          select.KQ_NOTE_LINK |
          select.KQ_NOTE_RENAME |
          select.KQ_NOTE_REVOKE)

'''
Watches Files and folder modification
When event is triggered, it class DirectorySnapshot class to see the change
Supports BSD and freeBSD
'''


class Gatekeeper(object):
    def __init__(self, dir_path):
        try:
            self._dir_path = dir_path
            self._snapshot = DirectorySnapshot(dir_path, False)
            self._file_descriptor = os.open(dir_path, DIR_OPEN_TYPE)
            self._event = kevent(self._file_descriptor, filter=FILTER,
                                 flags=FLAGS,
                                 fflags=FFLAGS)
            self._kq = kqueue()
            self._kq.control([self._event], 10000000, 0)

        except OSError, e:
            logging.error(e)
        except Exception, e:
            logging.error(e)

    def run(self):
        try:
            # Infinite loop for constantly checking the events
            while True:
                event_lookups = self._kq.control(None, 1)
                for event in event_lookups:
                    if event.fflags & select.KQ_NOTE_DELETE:
                        logging.info("Directory {0} is deleted".format(os.path.abspath(self._dir_path)))
                        return
                    elif event.fflags & select.KQ_NOTE_RENAME:
                        logging.info("File {0} is renamed".format(os.path.basename(self._dir_path)))
                    elif event.fflags & select.KQ_NOTE_EXTEND | select.KQ_NOTE_WRITE | select.KQ_NOTE_ATTRIB | select.KQ_NOTE_LINK | select.KQ_NOTE_REVOKE:
                        new_snapshot = DirectorySnapshot(self._dir_path, False)
                        diff_snapshot = DirectorySnapshotDiff(self._snapshot, new_snapshot)
                        messages = Message(diff_snapshot)
                        for message in messages.getMsg:
                            if not 'Moved' in message[1]:
                                for m in message[0]:
                                    logging.info('{0} {1}'.format(message[1], m))
                            else:
                                logging.info(
                                    '{0} from {1} to {2}'.format(message[1], message[0][0][0], message[0][0][1]))

                        self._snapshot = new_snapshot
        except KeyboardInterrupt:
            pass
        except Exception, e:
            logging.error(e)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info('File Watcher shutting down.........')
        os.close(self._file_descriptor)
        self._kq.close()
        time.sleep(1)


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath('.')
    f = Gatekeeper(path)
    with f:
        f.run()

