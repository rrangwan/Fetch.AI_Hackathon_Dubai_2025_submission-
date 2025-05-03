import json
import requests
from typing import Any
from env import WAVER_ADDRESS

def waver_generate_sound(text: str) -> str:

    payload ={
        "input_string": text,
    }

    response = requests.post(
        f"{WAVER_ADDRESS}/generate",
        data=json.dumps(payload),
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    # ASI1 returns choices[0].message.content (OpenAI-compatible)
    return data["download_link"]
