# Import necessary libraries
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS  # For handling Cross-Origin Resource Sharing
from pymongo import MongoClient
from datetime import datetime


# Initialize Flask app
app = Flask(__name__)
# CORS(app, resources={
#     r"/api/*": {
#         "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
#         "methods": ["GET", "POST", "OPTIONS"],
#         "allow_headers": ["Content-Type", "Authorization"]
#     }
# })



# Handle preflight OPTIONS requests for CORS
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,ngrok-skip-browser-warning")
        response.headers.add('Access-Control-Allow-Methods', "GET,POST,OPTIONS")
        return response

# Add CORS headers to actual responses (but check if they already exist)
@app.after_request
def after_request(response):
    # Only add headers if they don't already exist
    if not response.headers.get('Access-Control-Allow-Origin'):
        response.headers.add('Access-Control-Allow-Origin', '*')
    if not response.headers.get('Access-Control-Allow-Headers'):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,ngrok-skip-browser-warning')
    if not response.headers.get('Access-Control-Allow-Methods'):
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response


# Connect to MongoDB
client = MongoClient("mongodb+srv://webhookuser:12345@webhook.su9btta.mongodb.net/?retryWrites=true&w=majority&appName=webhook")
db = client["webhookDB"]
collection = db["events"]


# GitHub Webhook endpoint
@app.route('/github', methods=['POST'])
def webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')

    doc = {
        "author": "",
        "action": "",
        "request_id": "",
        "from_branch": "",
        "to_branch": "",
        "timestamp": ""
    }

    timestamp = datetime.utcnow().isoformat() + "Z"  # ISO UTC format string

    if event_type == "push":
        doc["author"] = data["pusher"]["name"]
        doc["action"] = "PUSH"
        doc["request_id"] = data["head_commit"]["id"]  # commit hash
        doc["from_branch"] = data["ref"].split("/")[-1]
        doc["to_branch"] = data["ref"].split("/")[-1]
        doc["timestamp"] = timestamp

    elif event_type == "pull_request":
        pr = data["pull_request"]
        author = pr["user"]["login"]
        from_branch = pr["head"]["ref"]
        to_branch = pr["base"]["ref"]
        action = data["action"]
        pr_id = str(pr["id"])

        if action == "opened":
            doc["author"] = author
            doc["action"] = "PULL REQUEST"
            doc["request_id"] = pr_id
            doc["from_branch"] = from_branch
            doc["to_branch"] = to_branch
            doc["timestamp"] = timestamp

        elif action == "closed" and pr["merged"]:
            doc["author"] = author
            doc["action"] = "MERGE"
            doc["request_id"] = pr_id
            doc["from_branch"] = from_branch
            doc["to_branch"] = to_branch
            doc["timestamp"] = timestamp

        else:
            return '', 200

    else:
        return '', 200

    collection.insert_one(doc)
    return jsonify({"status": "success"}), 200


# API to fetch all stored events from MongoDB
@app.route('/api/events', methods=['GET'])
def get_events():
    events = list(collection.find({}, {"_id": 0}))
    return jsonify(events)

# Start the Flask server
if __name__ == '__main__':
    app.run(debug=True, port=5000)
