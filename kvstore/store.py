import json
import os
import threading


class KVStore:
    def __init__(self, file_path):
        self.file_path = file_path  # The path to the JSON file on disk.
        self.lock = threading.Lock()  # A lock to manage concurrent access to the KV store.
        self.data = self._load_data_from_disk()  # Loads existing data or creates a new store.
        self.data["Campaigns"] = {}
        self.data["Articles"] = {}
        self.data["MDimValuesByDate"] = {}

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

    def get(self, key, type):
        # Retrieve a value from the KV store.
        with self.lock:
            if type == "Campaigns":
                return self.data["Campaigns"].get(key, None)
            elif type == "Articles":
                return self.data["Articles"].get(key, None)
            elif type == "MDimValuesByDate":
                return self.data["MDimValuesByDate"].get(key, None)

    def set(self, key, value, type):
        # Set a value in the KV store and persist changes to disk.
        with self.lock:
            obj = {key: value}
            if type == "Campaigns":
                self.data["Campaigns"].update(obj)
                self._persist_data_to_disk()
            elif type == "Articles":
                if key in self.data["Articles"]:
                    self.data["Articles"][key].update(value)
                else:
                    self.data["Articles"].update(obj)
                self._persist_data_to_disk()
            elif type == "MDimValuesByDate":
                self.data["MDimValuesByDate"].update(obj)
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
