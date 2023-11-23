import concurrent.futures
import requests
import time

URLS = [
    'http://www.foxnews.com/',
    'http://www.cnn.com/',
    'http://europe.wsj.com/',
    'http://www.bbc.co.uk/',
    'http://some-made-up-domain.com/'
]


# Retrieve a single page and report the URL and the length of the content
def load_url(url, timeout):
    with requests.get(url, timeout=timeout) as response:
        return url, response.content


def main():
    start_time = time.time()  # Capture start time

    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
                print(f"{url} page is {len(data[1])} bytes")
            except Exception as exc:
                print(f"{url} generated an exception: {exc}")

    end_time = time.time()  # Capture end time
    print(f"Runtime of the program is {end_time - start_time} seconds")


if __name__ == "__main__":
    main()
