# Main file will demonstrate the improved performance of the distributed system by comparing the time it takes to
# process 8 documents with a centralized system and the distributed system.
import concurrent.futures
import json

from kvstore.store import KVStore
from distributed_system.ds import DistributedSystem

if __name__ == '__main__':
    num_parallel_workers = 4

    # Initialize the shared KV store with a path to the JSON file.
    kv_store = KVStore('data/kv_store_data.json')

    # Load reviews from the data.json file
    with open('movie-review-data/data.json') as json_file:
        data = json.load(json_file)

    # Initialize the distributed system with 4 nodes.
    ds = DistributedSystem(kv_store, num_parallel_workers)

    # Create a campaign for the book "Killers of the Flower Moon".
    campaign_id = ds.create_campaign("What is the public perception of the movie, Killers of the Flower Moon by "
                                     "Martin Scorcese?")
    print(f"New campaign created with ID: {campaign_id}")

    # Prepare Review Data
    kotfm = data['killersOfTheFlowerMoon']
    kotfm_reviews = kotfm['reviews']

    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_parallel_workers) as executor:
        # Start the load operations and mark each future with its URL
        future_to_review = {executor.submit(ds.process_document, campaign_id, review["content"], review["id"], 60): review for review in kotfm_reviews}
        for future in concurrent.futures.as_completed(future_to_review):
            rev = future_to_review[future]
            try:
                data = future.result()
                print(f"{rev} review evaluated to {data}")
            except Exception as exc:
                print(f"{rev} generated an exception: {exc}")

