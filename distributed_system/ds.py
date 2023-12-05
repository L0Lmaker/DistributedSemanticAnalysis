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

    def query(self, campaign_id, date):
        node = self.get_node_from_load_balancer()
        return node.query(campaign_id, date)
