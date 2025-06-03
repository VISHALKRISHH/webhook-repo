# webhook-repo

This is the backend service built with **Flask** to receive GitHub webhook events from `action-repo`, parse them, and store the events in **MongoDB Atlas**.

> Front-end: https://github.com/VISHALKRISHH/webhook-ui/blob/main/src/App.js (react app)
> Front-end display: 
## 🧠 Features

- Receives webhooks for:
  - Push events
  - Pull Requests
  - Merge events
- Parses and stores the data in structured MongoDB schema
- Exposes a REST API for the frontend to poll every 15 seconds

## 📄 MongoDB Schema

```json
{
  "request_id": "c62a8e3...",        // commit hash or PR id
  "author": "vishalkrishh",          // GitHub user
  "action": "PUSH",                  // Enum: "PUSH", "PULL REQUEST", "MERGE"
  "from_branch": "dev",
  "to_branch": "main",
  "timestamp": "2025-06-02T15:00:00Z"
}

