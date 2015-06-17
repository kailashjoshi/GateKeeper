__author__ = 'Kailash Joshi'

from message import Message
from dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff
import sys
import signal
import logging
import os

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)d %(levelname)s %(process)s %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S")


def handler(signum, frame):
    logging.info("Shutting down with signal {0}".format(signum))
    sys.exit(0)


for sig in dir(signal):
    if sig.startswith("SIG"):
        try:
            signum = getattr(signal, sig)
            signal.signal(signum, handler)
        except Exception:
            pass

'''
Alternate approach of watching files/directory changes
Constantly checking snapshot of directory and looking for changes
'''


class Watcher(object):
    def __init__(self, path):
        self.path = path
        self._snapshot = DirectorySnapshot(path, True)

    def run(self):
        while True:
            try:
                new_snapshot = DirectorySnapshot(self.path, True)
                diff_snapshot = DirectorySnapshotDiff(self._snapshot, new_snapshot)
                messages = Message(diff_snapshot).getMsg
                if messages:
                    for message in messages:
                        if not 'Moved' in message[1]:
                            for m in message[0]:
                                logging.info('{0} {1}'.format(message[1], m))
                        else:
                            for m in message[0]:
                                logging.info('{0} from {1} to {2}'.format(message[1], m[0], m[1]))
                    self._snapshot = new_snapshot
            except OSError:
                pass
            except KeyboardInterrupt:
                pass


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath('.')
    w = Watcher(path)
    w.run()




