__author__ = 'Kailash Joshi'

'''
Extract message from DirectorySnapshotDiff class
'''


class Message(object):
    def __init__(self, diff):
        # diff is an instance of DirectorySnapshotDiff
        self.msg = []
        self.diff = diff

    @property
    def getMsg(self):
        # Collect message if list is not empty
        if self.diff._dirs_moved:
            self.msg.append((self.diff._dirs_moved, 'Directory Moved'))
        if self.diff._dirs_created:
            self.msg.append((self.diff._dirs_created, 'Directory Created'))
        if self.diff._dirs_modified:
            self.msg.append((self.diff.dirs_modified, 'Directory Modified'))
        if self.diff._dirs_deleted:
            self.msg.append((self.diff._dirs_deleted, 'Directory Deleted'))

        if self.diff._files_deleted:
            self.msg.append((self.diff._files_deleted, 'File Deleted'))
        if self.diff._files_modified:
            self.msg.append((self.diff._files_modified, 'File Modified'))
        if self.diff._files_moved:
            self.msg.append((self.diff._files_moved, 'File Moved'))
        if self.diff._files_created:
            self.msg.append((self.diff._files_created, 'File Created'))
        return self.msg


