"""Send malformed JSON to a locally running API and print the response.

Run from the repo root:  python -m scripts.check_invalid_json
"""

import requests

response = requests.post(
    "http://127.0.0.1:8000/analyze",
    data="{",
    headers={"Content-Type": "application/json"},
    timeout=10,
)

print("Status:", response.status_code)
print("Response:", response.text)
