"""Flask server for NarrativeWatch AI API."""

import logging
import os
from flask import Flask, request, jsonify
from src.api.routes import get_analysis_api, AnalyzePostRequest, AnalyzePageRequest
from src.agents.orchestrator import get_orchestrator
from src.agents.example_agents import get_example_agents

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# Initialize API
analysis_api = get_analysis_api()

# Register example agents (replace with actual implementations)
orchestrator = get_orchestrator()
bias_agent, bot_agent, misinformation_agent = get_example_agents()
orchestrator.register_bias_agent(bias_agent)
orchestrator.register_bot_agent(bot_agent)
orchestrator.register_misinformation_agent(misinformation_agent)

logger.info("✓ Flask server initialized with all agents")


# ==================== ROUTES ====================


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint.

    Returns:
        System health status
    """
    try:
        health_status = analysis_api.health_check()
        return jsonify(health_status), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


@app.route("/stats", methods=["GET"])
def stats():
    """Get RAG pipeline statistics.

    Returns:
        RAG statistics
    """
    try:
        stats_data = analysis_api.get_rag_stats()
        return jsonify({"status": "success", "data": stats_data}), 200
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/analyze/post", methods=["POST"])
def analyze_post():
    """Analyze Instagram post.

    Request JSON:
    {
        "post_id": "123",
        "page_username": "user",
        "caption": "Post text",
        "hashtags": ["#tag1", "#tag2"],
        "likes": 100,
        "comments": 10
    }

    Returns:
        Comprehensive analysis with risk level and recommendations
    """
    try:
        data = request.get_json()

        # Check if data is None
        if data is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": "Request body must be valid JSON",
                    }
                ),
                400,
            )

        # Validate required fields
        required = ["post_id", "page_username", "caption"]
        if not all(field in data for field in required):
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": f"Missing required fields: {required}",
                    }
                ),
                400,
            )

        # Create request
        analysis_request = AnalyzePostRequest(
            post_id=data["post_id"],
            page_username=data["page_username"],
            caption=data["caption"],
            hashtags=data.get("hashtags", []),
            likes=data.get("likes", 0),
            comments=data.get("comments", 0),
        )

        # Analyze
        logger.info(f"POST /analyze/post - Post {data['post_id']}")
        response = analysis_api.analyze_post(analysis_request)

        return (
            jsonify(
                {
                    "status": "success",
                    "data": response.dict(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error analyzing post: {e}")
        return (
            jsonify({"status": "error", "error": str(e)}),
            500,
        )


@app.route("/analyze/page", methods=["POST"])
def analyze_page():
    """Analyze Instagram page.

    Request JSON:
    {
        "page_id": "page_123",
        "username": "user",
        "biography": "Page bio",
        "followers": 10000
    }

    Returns:
        Comprehensive page analysis
    """
    try:
        data = request.get_json()

        # Check if data is None
        if data is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": "Request body must be valid JSON",
                    }
                ),
                400,
            )

        # Validate required fields
        required = ["page_id", "username"]
        if not all(field in data for field in required):
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": f"Missing required fields: {required}",
                    }
                ),
                400,
            )

        # Create request
        analysis_request = AnalyzePageRequest(
            page_id=data["page_id"],
            username=data["username"],
            biography=data.get("biography"),
            followers=data.get("followers", 0),
        )

        # Analyze
        logger.info(f"POST /analyze/page - Page {data['username']}")
        response = analysis_api.analyze_page(analysis_request)

        return (
            jsonify(
                {
                    "status": "success",
                    "data": response.dict(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error analyzing page: {e}")
        return (
            jsonify({"status": "error", "error": str(e)}),
            500,
        )


# ==================== ERROR HANDLERS ====================


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return (
        jsonify(
            {
                "status": "error",
                "error": "Endpoint not found",
                "available_endpoints": ["/health", "/stats", "/analyze/post", "/analyze/page"],
            }
        ),
        404,
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return (
        jsonify(
            {
                "status": "error",
                "error": "Internal server error",
            }
        ),
        500,
    )


# ==================== LOGGING ====================


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Get port from environment
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "False").lower() == "true"

    logger.info(f"🚀 Starting NarrativeWatch AI server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
