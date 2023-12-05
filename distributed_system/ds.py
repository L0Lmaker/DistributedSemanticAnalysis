# Distributed system class that will be used to process documents, create campaigns and read data in parallel.
from node.node import Node


class DistributedSystem:
    def __init__(self, kv_store, num_nodes):
        self.kv_store = kv_store  # KVStore object for storage operations.
        self.nodes = {}
        self.num_nodes = num_nodes
        self.load_balancer_index = 0

        # Create nodes
        for i in range(num_nodes):
            self.nodes[i] = Node(kv_store, i)

    def get_node_from_load_balancer(self):
        self.load_balancer_index = (self.load_balancer_index + 1) % self.num_nodes
        return self.nodes[self.load_balancer_index]

    def create_campaign(self, topic):
        node = self.get_node_from_load_balancer()
        return node.create_campaign(topic)

    def process_document(self, campaign_id, document, article_id, published_date):
        node = self.get_node_from_load_balancer()
        return node.process_document(campaign_id, document, article_id, published_date)

    def get_by_date(self, campaign_id, date):
        node = self.get_node_from_load_balancer()
        return node.get_by_date(campaign_id, date)

    def get_by_article_id(self, campaign_id, article_id):
        node = self.get_node_from_load_balancer()
        return node.get_by_article_id(campaign_id, article_id)

    def get_campaign_details(self, campaign_id):
        node = self.get_node_from_load_balancer()
        return node.get_campaign_details(campaign_id)

    def get_campaign_id_list(self):
        node = self.get_node_from_load_balancer()
        return node.get_campaign_id_list()

    def get_article_ids_for_campaign(self, campaign_id):
        node = self.get_node_from_load_balancer()
        return node.get_article_ids_for_campaign(campaign_id)

    def get_date_list(self, campaign_id):
        node = self.get_node_from_load_balancer()
        return node.get_date_list(campaign_id)
