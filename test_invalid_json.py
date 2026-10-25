
import requests

response = requests.post(
    "http://127.0.0.1:8000/analyze",
    data="{",
    headers={"Content-Type": "application/json"}
)

print("Status:", response.status_code)
print("Response:", response.text)
