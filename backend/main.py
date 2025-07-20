from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn
import github_client
import llm_client

# --- Pydantic Models ---
# A generic model to accept any valid JSON from GitHub's webhook
class GitHubWebhookPayload(BaseModel):
    pass

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Docu-Mentor Backend",
    version="0.3.0"
)

def process_pull_request(payload: dict):
    """
    The main background task to analyze a PR and post documentation suggestions.
    """
    installation_id = payload.get("installation", {}).get("id")
    pull_request_data = payload.get("pull_request", {})
    pr_number = pull_request_data.get("number")
    repo_name = payload.get("repository", {}).get("full_name")

    print(f"Processing PR #{pr_number} in repo {repo_name}.")

    # 1. Get an installation access token
    token = github_client.get_installation_access_token(installation_id)
    if not token:
        print("Error: Could not get installation access token.")
        return

    # 2. Get the diff for the pull request
    diff = github_client.get_pull_request_diff(repo_name, pr_number, token)
    if not diff:
        print("Error: Could not fetch PR diff.")
        return

    # 3. Parse the diff to find new functions
    new_functions = github_client.parse_diff_for_new_functions(diff)
    if not new_functions:
        print("No new functions found in the PR diff.")
        return

    print(f"Found {len(new_functions)} new functions to document.")

    # 4. Generate docstrings for each new function
    suggestions = []
    for func in new_functions:
        print(f"Generating docstring for function: {func['name']}")
        docstring = llm_client.generate_docstring_for_function(func['code'])
        if docstring:
            suggestion = (
                f"### Suggestion for `{func['name']}`\n\n"
                "```python\n"
                f"{docstring}\n"
                "```"
            )
            suggestions.append(suggestion)

    # 5. Post a comment if there are any suggestions
    if suggestions:
        comment_body = (
            "**Docu-Mentor** found some functions that could use documentation:\n\n---\n\n" +
            "\n\n---\n\n".join(suggestions)
        )
        github_client.post_comment_on_pr(repo_name, pr_number, comment_body, token)
    else:
        print("No docstrings could be generated.")

# --- API Endpoints ---
@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/api/v1/webhook/github", tags=["Webhooks"])
async def receive_github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None)
):
    """
    Receives, verifies, and processes webhook events from the GitHub App.
    """
    raw_body = await request.body()

    # 1. Verify the webhook signature
    if not github_client.verify_github_signature(raw_body, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid signature.")

    payload = await request.json()
    print(f"Successfully received and verified GitHub event: '{x_github_event}'")

    # 2. Process only 'pull_request' events that are 'opened' or 'reopened'
    if x_github_event == "pull_request":
        action = payload.get("action")
        print(f"DEBUG: Pull request action is '{action}'.")
    
    # We will check against a wider range of actions
        if action in ["opened", "synchronize", "reopened", "ready_for_review"]:
            print(f"Action '{action}' is valid. Adding task to background.")
            background_tasks.add_task(process_pull_request, payload)
        else:
            print(f"Action '{action}' is not one we process. Skipping.")
    else:
        print(f"Event '{x_github_event}' is not a pull request. Skipping.")

    return {"status": "success", "event_received": x_github_event}

# --- Main Entry Point ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 