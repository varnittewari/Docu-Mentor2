from fastapi import FastAPI, Request, Header
from pydantic import BaseModel
import uvicorn

# --- Pydantic Models ---
# A generic model to accept any valid JSON from GitHub's webhook
class GitHubWebhookPayload(BaseModel):
    pass

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Docu-Mentor Backend",
    description="Handles GitHub webhooks and processes code for documentation generation.",
    version="0.1.0"
)

# --- API Endpoints ---
@app.get("/health", tags=["Monitoring"])
async def health_check():
    """
    Health check endpoint to verify service is running.
    """
    return {"status": "ok"}

@app.post("/api/v1/webhook/github", tags=["Webhooks"])
async def receive_github_webhook(payload: dict, x_github_event: str = Header(None)):
    """
    Receives webhook events from the Docu-Mentor GitHub App.
    """
    print(f"Received GitHub event: '{x_github_event}'")
    # In later phases, we will add verification and processing logic here.
    print("Webhook received and acknowledged.")
    return {"status": "success", "event_received": x_github_event}

# --- Main Entry Point ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 