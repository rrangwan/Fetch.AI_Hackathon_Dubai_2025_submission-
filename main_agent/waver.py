import json
import requests
from typing import Any
from env import WAVER_ADDRESS

def waver_generate_sound(text: str) -> str:

    payload ={
        "input_string": text,
    }

    headers = {
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"http://{WAVER_ADDRESS}/generate_wav",
        data=json.dumps(payload),
        headers=headers,
        timeout=60,
        stream=True
    )
    response.raise_for_status()
    data = response.json()
    # ASI1 returns choices[0].message.content (OpenAI-compatible)
    return data["download_link"]
