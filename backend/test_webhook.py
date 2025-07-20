import requests
import hmac
import hashlib
import json
from config import GITHUB_WEBHOOK_SECRET

# Test payload simulating a pull request event
payload = {
    "action": "opened",
    "installation": {"id": 12345},
    "pull_request": {"number": 1},
    "repository": {"full_name": "test-org/test-repo"}
}

# Convert payload to JSON string
body = json.dumps(payload).encode('utf-8')

# Calculate signature
signature = hmac.new(
    GITHUB_WEBHOOK_SECRET.encode('utf-8'),
    msg=body,
    digestmod=hashlib.sha256
).hexdigest()

# Headers
headers = {
    'X-GitHub-Event': 'pull_request',
    'X-Hub-Signature-256': f'sha256={signature}',
    'Content-Type': 'application/json'
}

# Send request
response = requests.post(
    'http://localhost:8000/api/v1/webhook/github',
    data=body,
    headers=headers
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}") 