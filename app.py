from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import logging
import os
import time


# --- Metrics ---
REQUEST_COUNT = Counter(
    "flask_request_count",
    "Total number of requests",
    ["method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    "flask_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"]
)


def create_app():
    app = Flask(__name__)

    # --- Logging ---
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    # --- Middleware: Track metrics before/after request ---
    @app.before_request
    def before_request():
        request.start_time = time.time()

    @app.after_request
    def after_request(response):
        latency = time.time() - request.start_time

        REQUEST_LATENCY.labels(request.endpoint).observe(latency)
        REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()

        return response

    # --- Routes ---
    @app.route("/")
    def home():
        app.logger.info("Home endpoint accessed")
        return jsonify(message="Hello from customer-orders-service service!", status="OK")

    @app.route("/health")
    def health():
        return jsonify(status="healthy", service="customer-orders-service")

    @app.route("/metrics")
    def metrics():
        return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

    return app


if __name__ == "__main__":
    app = create_app()

    host = os.getenv("SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("SERVICE_PORT", 5000))

    app.run(host=host, port=port)
