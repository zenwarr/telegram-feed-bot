import os
from prometheus_client import start_http_server, Counter


def init_metrics():
    metrics_enabled = os.environ.get("ENABLE_METRICS")
    if metrics_enabled is not None and metrics_enabled.lower() == "true":
        start_http_server(
            addr=os.environ.get("METRICS_SERVER_HOST", "0.0.0.0"),
            port=os.environ.get("METRICS_SERVER_PORT", "8080"),
        )


MESSAGES_SENT = Counter("messages_sent", "Number of messages sent")
