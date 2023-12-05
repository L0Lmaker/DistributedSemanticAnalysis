import json
import os
import threading


class KVStore:
    def __init__(self, file_path):
        self.file_path = file_path  # The path to the JSON file on disk.
        self.lock = threading.Lock()  # A lock to manage concurrent access to the KV store.
        self.data = self._load_data_from_disk()  # Loads existing data or creates a new store.
        self.data.setdefault("Campaigns", {})
        self.data.setdefault("Articles", {})
        self.data.setdefault("MDimValuesByDate", {})

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

    def get_campaign_details(self, campaign_id):
        with self.lock:
            return self.data["Campaigns"][campaign_id]

    def get_campaign_id_list(self):
        with self.lock:
            keys_list = list(self.data["Campaigns"].keys())
            return keys_list

    def get_article_ids_for_campaign(self, campaign_id):
        with self.lock:
            keys_list = list(self.data["Articles"][campaign_id].keys())
            return keys_list

    def get_by_date(self, campaign_id, date):
        with self.lock:
            return self.data["MDimValuesByDate"][campaign_id][date]

    def get_date_list(self, campaign_id):
        with self.lock:
            keys_list = list(self.data["MDimValuesByDate"][campaign_id].keys())
            return keys_list

    def get_by_article(self, campaign_id, article_id):
        with self.lock:
            return self.data["Articles"][campaign_id][article_id]

    def set_campaign(self, campaign_id, campaign_data):
        obj = {campaign_id: campaign_data}
        self.data["Campaigns"].update(obj)
        self._persist_data_to_disk()

    def set_article(self, campaign_id, article_id, article_data):
        self.data["Articles"].setdefault(campaign_id, {})
        self.data["Articles"][campaign_id].update(article_data)
        self._persist_data_to_disk()

    def set_mdim_by_date(self, campaign_id, publish_date, article_id, mdim_data):
        obj = {article_id: mdim_data}
        self.data["MDimValuesByDate"].setdefault(campaign_id, {})
        self.data["MDimValuesByDate"][campaign_id].setdefault(publish_date, {})
        self.data["MDimValuesByDate"][campaign_id][publish_date].update(obj)
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
