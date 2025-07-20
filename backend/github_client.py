import time
import hmac
import hashlib
import jwt
import requests
import re
import config

def verify_github_signature(request_body: bytes, signature_header: str) -> bool:
    """
    Verify the signature of an incoming GitHub webhook.

    Args:
        request_body: The raw request body.
        signature_header: The value of the 'X-Hub-Signature-256' header.

    Returns:
        True if the signature is valid, False otherwise.
    """
    if not signature_header:
        print("Error: X-Hub-Signature-256 header is missing.")
        return False

    hash_object = hmac.new(
        config.GITHUB_WEBHOOK_SECRET.encode('utf-8'),
        msg=request_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()

    return hmac.compare_digest(expected_signature, signature_header)

def create_github_jwt() -> str:
    """
    Create a JSON Web Token (JWT) to authenticate as the GitHub App.

    Returns:
        The generated JWT as a string.
    """
    with open(config.GITHUB_PRIVATE_KEY_PEM_PATH, 'r') as f:
        private_key = f.read()

    payload = {
        'iat': int(time.time()),
        'exp': int(time.time()) + (10 * 60),  # 10 minute expiration
        'iss': config.GITHUB_APP_ID
    }

    return jwt.encode(payload, private_key, algorithm='RS256')

def get_installation_access_token(installation_id: int) -> str | None:
    """
    Get an installation access token for a specific repository.

    Args:
        installation_id: The ID of the app installation.

    Returns:
        The access token string, or None if an error occurs.
    """
    app_jwt = create_github_jwt()
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github.v3+json",
    }
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"

    response = requests.post(url, headers=headers)

    if response.status_code == 201:
        return response.json().get('token')
    else:
        print(f"Error getting access token: {response.status_code} {response.text}")
        return None

def get_pull_request_diff(repo_full_name: str, pr_number: int, token: str) -> str | None:
    """
    Fetches the diff for a specific pull request.

    Args:
        repo_full_name: The full name of the repository (e.g., 'owner/repo').
        pr_number: The number of the pull request.
        token: The installation access token.

    Returns:
        The diff content as a string, or None on failure.
    """
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error fetching PR diff: {response.status_code} {response.text}")
        return None

def parse_diff_for_new_functions(diff: str) -> list[dict]:
    """
    Parses a diff to find newly added Python functions.

    Args:
        diff: The diff content as a string.

    Returns:
        A list of dictionaries, where each dictionary contains the
        function name and its code block.
    """
    new_functions = []
    # Regex to find the start of a new Python function in a diff
    function_def_pattern = re.compile(r'^\+\s*def\s+([a-zA-Z_]\w*)\s*\(')

    current_function_name = None
    current_function_code = []

    lines = diff.split('\n')
    for i, line in enumerate(lines):
        if current_function_name:
            # Continue capturing lines until the block ends
            if line.startswith('+') and not line.startswith('+++'):
                # Check indentation to handle nested functions (basic check)
                if len(line) - len(line.lstrip(' +')) > 0:
                    current_function_code.append(line[1:])
                else: # End of block
                    new_functions.append({
                        "name": current_function_name,
                        "code": "\n".join(current_function_code)
                    })
                    current_function_name = None
                    current_function_code = []
            else: # End of block
                new_functions.append({
                    "name": current_function_name,
                    "code": "\n".join(current_function_code)
                })
                current_function_name = None
                current_function_code = []

        match = function_def_pattern.match(line)
        if match:
            # If we find a new function, start capturing it
            if current_function_name: # Save previous function if any
                 new_functions.append({
                    "name": current_function_name,
                    "code": "\n".join(current_function_code)
                })
            current_function_name = match.group(1)
            current_function_code = [line[1:]] # Start with the def line

    if current_function_name: # Save the last function
        new_functions.append({
            "name": current_function_name,
            "code": "\n".join(current_function_code)
        })

    return new_functions

def post_comment_on_pr(repo_full_name: str, pr_number: int, comment_body: str, token: str):
    """
    Posts a comment on a GitHub pull request.

    Args:
        repo_full_name: The full name of the repository.
        pr_number: The number of the pull request.
        comment_body: The markdown content of the comment.
        token: The installation access token.
    """
    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"body": comment_body}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"Successfully posted comment on PR #{pr_number}.")
    else:
        print(f"Error posting comment: {response.status_code} {response.text}") 