"""
Utilities for finding the newest file and waiting for it to finish.
"""
import os
import time

def get_newest_file(path):
    """
    Find the newest file in the path. There should be a more direct way to find
    the new download, but I'm not sure how.
    """
    return max(
        (os.path.join(path, f) for f in os.listdir(path)),
        key=os.path.getctime
    )


def wait_for_file_to_finish(filename):
    """
    Wait for a file to finish. It is somewhat naive, and just checks the file
    size every second until it doesn't change.
    """
    size = -1
    newsize = os.path.getsize(filename)
    while size != newsize:
        print('size:', size, 'newsize:', newsize)
        size = newsize
        time.sleep(1)
        newsize = os.path.getsize(filename)
