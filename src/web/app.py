"""
Flask web application for RepoDocGen documentation interface
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import re

from src.config import Config

def inline_code_filter(text: str) -> str:
    """Convert `inline code` into HTML spans with code-pill class."""
    if not text:
        return text
    return re.sub(r"`([^`]+)`", r'<span class="code-pill">\1</span>', text)

def create_app(qa_bot=None, repo_summary=None, file_summaries=None):
    """Create and configure Flask app"""
    app = Flask(__name__)
    CORS(app)

    # Register Jinja filter for inline code
    app.jinja_env.filters["inline_code"] = inline_code_filter

    # Store components in app config
    app.config["QA_BOT"] = qa_bot
    app.config["REPO_SUMMARY"] = repo_summary
    app.config["FILE_SUMMARIES"] = file_summaries or []

    # Store components in app config
    app.config["QA_BOT"] = qa_bot
    app.config["REPO_SUMMARY"] = repo_summary
    app.config["FILE_SUMMARIES"] = file_summaries or []

    @app.route("/")
    def index():
        """Main documentation page"""
        return render_template(
            "index.html",
            repo_summary=app.config["REPO_SUMMARY"],
            file_summaries=app.config["FILE_SUMMARIES"],
        )

    @app.route("/api/query", methods=["POST"])
    def query():
        """Handle chatbot queries"""
        data = request.json
        question = data.get("question", "")

        if not question:
            return jsonify({"error": "No question provided"}), 400

        qa_bot = app.config["QA_BOT"]
        if not qa_bot:
            return jsonify({"error": "QA bot not initialized"}), 500

        try:
            result = qa_bot.query(question)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/files")
    def get_files():
        """Get list of all files"""
        summaries = app.config["FILE_SUMMARIES"]
        files = [
            {
                "path": s.file_path,
                "language": s.language,
                "summary": s.high_level_summary,
            }
            for s in summaries
        ]
        return jsonify(files)

    @app.route("/api/file/<path:filepath>")
    def get_file_details(filepath):
        """Get detailed info about a specific file"""
        summaries = app.config["FILE_SUMMARIES"]

        for summary in summaries:
            if summary.file_path == filepath:
                return jsonify(
                    {
                        "file_path": summary.file_path,
                        "language": summary.language,
                        "summary": summary.high_level_summary,
                        "functionalities": summary.main_functionalities,
                        "key_elements": summary.key_elements,
                        "dependencies": summary.dependencies,
                    }
                )

        return jsonify({"error": "File not found"}), 404

    @app.route("/health")
    def health():
        """Health check endpoint"""
        return jsonify({"status": "healthy"})

    return app


def main():
    """Run the Flask app"""
    print("Starting RepoDocGen web interface...")
    print(f"Open http://localhost:{Config.FLASK_PORT} in your browser")

    app = create_app()
    app.run(
        host="0.0.0.0",
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG,
    )


if __name__ == "__main__":
    main()
