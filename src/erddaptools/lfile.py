import pathlib
import time
import uuid


class LockedFile:

    def __init__(self, path, retries=0, delay=0.5):
        self.path = pathlib.Path(path)
        self.lock_file = self.path.parent / (self.path.name + ".lock")
        self.retries = retries
        self.delay = delay

    def __enter__(self):
        access_key = f"{uuid.uuid4()}.{time.time()}"
        tries = self.retries + 1
        while tries > 0:
            try:
                success = False
                if not self.lock_file.exists():
                    with open(self.lock_file, "w") as h:
                        h.write(access_key)
                    with open(self.lock_file, "r") as h:
                        if h.read() == access_key:
                            success = True
                if success:
                    return self.path
            except (IOError, OSError):
                pass
            tries -= 1
            if tries > 0:
                time.sleep(self.delay)
        raise IOError(f"Could not obtain lock file on {self.path}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock_file.unlink(True)
