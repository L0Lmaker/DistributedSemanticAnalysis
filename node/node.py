import uuid
import datetime

from DistributedSemanticAnalysis.kvstore.store import KVStore


class Node:
    def __init__(self, kv_store, id):
        self.kv_store = kv_store  # KVStore object for storage operations.
        self.id = id

    def create_campaign(self, topic):
        campaign_id = str(uuid.uuid4())  # Generate a unique campaign identifier.
        campaign_data = {
            "topic": topic,
            "created_at": datetime.datetime.now().isoformat(),
            "MDims": self.get_dimensions("fake")  # Empty MDims, assuming initialization without data.
        }
        self.kv_store.set(campaign_id, campaign_data, "Campaigns")
        return campaign_id

    def process_document(self, campaign_id, document, article_id, published_date):
        # Implement the logic to assess the document and update MDims per campaign.
        # For now, this code assumes a placeholder function `analyze_document` exists.
        mdim_values = self.analyze_document(document)

        # Get existing campaign data
        campaign_data = self.kv_store.get(campaign_id, "Campaigns")
        if not campaign_data:
            return False, "Campaign not found"
        article = {article_id: mdim_values}
        # Persist the updated data
        self.kv_store.set(campaign_id, article, "Articles")
        #TODO add logic for MDimValuesByDate HERE, self.kv_store.set(campaign_id, sumDateStuff, "MDimValuesByDate")

        return True, campaign_data["MDims"]

    def query(self, campaign_id, date):
        campaign_data = self.kv_store.get(campaign_id, "Articles")
        if not campaign_data:
            return None
        return campaign_data


    def get_dimensions(self, topic):
        return [
        "direction_quality",
        "storytelling",
        "casting_performance",
        "cinematography",
        "historical_accuracy"
        ]
    def analyze_document(self, document):
        # This would be replaced by actual analysis logic to extract MDims.
        # For the prototype, you can simulate with either static values or random generation.
        return {
            "direction_quality": 0.75,
            "storytelling": 0.85,
            "casting_performance": 0.65,
            "cinematography": 0.90,
            "historical_accuracy": 0.80
        }


# Usage Example
# Assuming the KVStore class has been initialized as shown previously
kv_store = KVStore('kv_store_data.json')
node = Node(kv_store, 1)

# Create a new campaign
campaign_id = node.create_campaign("Killers of the Flower Moon")
print(f"New campaign created with ID: {campaign_id}")

# Process a document
success, new_mdims = node.process_document(campaign_id, "Document content...", "hi", "2023-04-01")
success2, new_mdims2 = node.process_document(campaign_id, "Document content...2", "hi2", "2023-04-01")
success1, new_mdims1 = node.process_document(campaign_id, "Document content...", "hi", "2023-04-01")
print(f"Document processed successfully: {success}, MDims: {new_mdims}")

# Query campaign data
mdims = node.query(campaign_id, "2023-04-01")
print(f"Queried MDims: {mdims}")