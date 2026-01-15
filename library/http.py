import httpx
from library.torbox import TORBOX_API_KEY
import time
import logging

TORBOX_API_URL = "https://api.torbox.app/v1/api"
TORBOX_SEARCH_API_URL = "https://search-api.torbox.app"
USER_AGENT = "TorBox-Media-Center/1.4 TorBox/1.0"

transport = httpx.HTTPTransport(
    retries=10
)

api_http_client = httpx.Client(
    base_url=TORBOX_API_URL,
    headers={
        "Authorization": f"Bearer {TORBOX_API_KEY}",
        "User-Agent": USER_AGENT,
    },
    timeout=httpx.Timeout(60),
    follow_redirects=True,
    transport=transport
)

search_api_http_client = httpx.Client(
    base_url=TORBOX_SEARCH_API_URL,
    headers={
        "Authorization": f"Bearer {TORBOX_API_KEY}",
        "User-Agent": USER_AGENT,
    },
    timeout=httpx.Timeout(60),
    follow_redirects=True,
    transport=transport,
)

general_http_client = httpx.Client(
    headers={
        "Authorization": f"Bearer {TORBOX_API_KEY}",
        "User-Agent": USER_AGENT,
    },
    timeout=httpx.Timeout(60),
    follow_redirects=False,
    transport=transport,
)

def requestWrapper(client: httpx.Client, method: str, url: str, **kwargs) -> httpx.Response:
    max_retries = 5
    backoff_factor = 1.5
    for attempt in range(max_retries):
        try:
            response = client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            bad_response_codes = [429]
            if e.response.status_code in bad_response_codes:
                wait_time = backoff_factor * (2 ** attempt)
                logging.warning(f"Received {e.response.status_code} for {url}. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                logging.error(f"HTTP error for {url}: {e}")
                raise
        except httpx.RequestError as e:
            wait_time = backoff_factor * (2 ** attempt)
            logging.warning(f"Request error on {url}: {e}. Retrying in {wait_time:.2f} seconds...")
            time.sleep(wait_time)
    raise httpx.RequestError(f"Failed to complete request to {url} after {max_retries} attempts.")
