import json
import os
import threading


class KVStore:
    def __init__(self, file_path):
        self.file_path = file_path  # The path to the JSON file on disk.
        self.lock = threading.Lock()  # A lock to manage concurrent access to the KV store.
        self.data = self._load_data_from_disk()  # Loads existing data or creates a new store.

    def _load_data_from_disk(self):
        if os.path.isfile(self.file_path):
            with open(self.file_path, 'r') as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return {}
        else:
            return {}

    def _persist_data_to_disk(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file, indent=4)

    def get(self, key):
        # Retrieve a value from the KV store.
        with self.lock:
            return self.data.get(key, None)

    def set(self, key, value):
        # Set a value in the KV store and persist changes to disk.
        with self.lock:
            self.data[key] = value
            self._persist_data_to_disk()

    def delete(self, key):
        # Remove a key from the KV store if it exists and persist changes to disk.
        with self.lock:
            if key in self.data:
                del self.data[key]
                self._persist_data_to_disk()


'''
# Usage
# Initialize the shared KV store with a path to the JSON file.
kv_store = SharedKVStore('kv_store_data.json')

# Set some values
kv_store.set('campaign_1', {'topic': 'Killers of the Flower Moon', 'MDims': {}})

# Get a value
campaign_data = kv_store.get('campaign_1')
print(campaign_data)

# Delete a key
kv_store.delete('campaign_1')

# At this point, because the class automatically persists changes to disk,
# all changes made to the kv_store will be reflected in 'kv_store_data.json'file.
'''
