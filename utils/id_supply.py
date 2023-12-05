import threading


class IdSupplier:
    """
    A class to supply unique IDs.
    """
    _id = 0
    _lock = threading.Lock()

    @staticmethod
    def get_id():
        """
        Returns a unique ID in a thread-safe way.
        """
        with IdSupplier._lock:
            IdSupplier._id += 1
            return IdSupplier._id
