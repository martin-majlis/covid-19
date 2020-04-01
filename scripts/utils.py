import os
import time
from typing import IO

import requests


def download(url: str, path: str, cache_lifetime=3600) -> IO:
    if not os.path.exists(path) or os.path.getmtime(path) < time.time() - cache_lifetime:
        response = requests.get(url, allow_redirects=True)
        print(f"Downloading {url} into {path}")
        with open(path, 'w') as fh:
            fh.write(response.text)
    print(f"{url} => {path}")
    return open(path, 'r')