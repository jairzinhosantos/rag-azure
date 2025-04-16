import os
import logging
import sys
import uuid
import asyncio
from flask import Flask, jsonify, request, render_template, session
from flask_cors import CORS
from orchestrator import Orchestrator
from config.config import Config
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Flask application
#app = Flask(__name__)
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv("FLASK_SECRET_KEY")

CORS(app)

# Initialize handler
config = Config().config
orchestrator = Orchestrator()

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/chat", methods=["POST"])
def chat():
    """Endpoint for handling chat requests."""
    try:
        logger.info("Processing chat request...")

        data = request.get_json(force=True)  # force=True helps avoid errors if the mimetype is not application/json
        if not data:
            logger.error("No se recibió JSON en la solicitud.")
            return jsonify({"error": "No se recibió JSON en la solicitud."}), 400
        
        logger.info(f"Received data: {data}")

        session_id = data.get('sessionID') or session.get('sessionID')

        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id

        query = data.get('query')
        if not query:
            logger.error("Missing 'query' in the request.")
            return jsonify({"error": "Missing 'query' in the request."}), 400

        response = asyncio.run(orchestrator.run(session_id, query))
        return response
    except KeyError as e:
        logger.error(f"Missing key in JSON data: {e}")
        return jsonify({"error": f"Missing key in JSON data: {e}"}), 400
    except Exception as e:
        logger.error(f"Error during chat processing: {e}")
        return jsonify({"error": str(e)}), 500

def start_app():
    """Starts the Flask application."""
    app.run(host=config["flask"]["host"], port=config["flask"]["port"], debug=True)

if __name__ == "__main__":
    start_app()