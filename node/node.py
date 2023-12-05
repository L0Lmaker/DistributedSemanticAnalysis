import uuid
import datetime
import random
import time
from kvstore.store import KVStore
from utils.id_supply import IdSupplier


class Node:
    def __init__(self, kv_store, id):
        self.kv_store = kv_store  # KVStore object for storage operations.
        self.id = id

    def create_campaign(self, topic):
        campaign_id = str(IdSupplier.get_id())  # Generate a unique campaign identifier.
        campaign_data = {
            "topic": topic,
            "created_at": datetime.datetime.now().isoformat(),
            # Empty MDims, assuming initialization without data.
            "MDims": self.get_dimensions_for_topic(topic)
        }
        self.kv_store.set_campaign(campaign_id, campaign_data)
        return campaign_id

    def process_document(self, campaign_id, document, article_id, published_date):
        # Implement the logic to assess the document and update MDims per campaign.
        # For now, this code assumes a placeholder function `analyze_document` exists.
        mdim_values = self.get_dimension_values_for_document(campaign_id, document)

        # Get existing campaign data
        campaign_data = self.kv_store.get_campaign_details(campaign_id)
        if not campaign_data:
            return False, "Campaign not found"
        article_processed = {
            article_id: mdim_values
        }
        # Persist the updated data
        self.kv_store.set_article(campaign_id, article_id, article_processed)
        self.kv_store.set_mdim_by_date(campaign_id, published_date, article_id, mdim_values)
        return True, article_processed

    def get_by_date(self, campaign_id, date):
        campaign_data = self.kv_store.get_by_date(campaign_id, date)
        if not campaign_data:
            return None
        return campaign_data

    def get_by_article_id(self, campaign_id, article_id):
        campaign_data = self.kv_store.get_by_article(campaign_id, article_id)
        if not campaign_data:
            return None
        return campaign_data

    def get_campaign_details(self, campaign_id):
        campaign_data = self.kv_store.get_campaign_details(campaign_id)
        if not campaign_data:
            return None
        return campaign_data

    def get_campaign_id_list(self):
        campaign_data = self.kv_store.get_campaign_id_list()
        if not campaign_data:
            return None
        return campaign_data

    def get_article_ids_for_campaign(self, campaign_id):
        campaign_data = self.kv_store.get_article_ids_for_campaign(campaign_id)
        if not campaign_data:
            return None
        return campaign_data

    def get_date_list(self, campaign_id):
        campaign_data = self.kv_store.get_date_list(campaign_id)
        if not campaign_data:
            return None
        return campaign_data

    def get_dimensions_for_topic(self, topic):
        # TODO: make call to GPT to get dimensions from topic
        return [
            "direction_quality",
            "storytelling",
            "casting_performance",
            "cinematography",
            "historical_accuracy"
        ]

    def get_dimension_values_for_document(self, campaign_id, article_content):
        # This would be replaced by actual analysis logic to extract MDims.
        # For the prototype, you can simulate with either static values or random generation.

        # Random Delay for testing
        time.sleep(random.randint(1, 5))
        return {
            "direction_quality": random.random(),
            "storytelling": random.random(),
            "casting_performance": random.random(),
            "cinematography": random.random(),
            "historical_accuracy": random.random()
        }


# # Usage Example
# # Assuming the KVStore class has been initialized as shown previously
# kv_store = KVStore('kv_store_data.json')
# node = Node(kv_store, 1)
#
# # Create a new campaign
# campaign_id = node.create_campaign("Killers of the Flower Moon")
# print(f"New campaign created with ID: {campaign_id}")
#
# # Process a document
# success, new_mdims = node.process_document(campaign_id, "Document content...", "hi", "2023-04-01")
# success2, new_mdims2 = node.process_document(campaign_id, "Document content...2", "hi2", "2023-04-01")
# success1, new_mdims1 = node.process_document(campaign_id, "Document content...", "hi", "2023-04-01")
# print(f"Document processed successfully: {success}, MDims: {new_mdims}")
#
# # Query campaign data
# mdims = node.query(campaign_id, "2023-04-01")
# print(f"Queried MDims: {mdims}")
