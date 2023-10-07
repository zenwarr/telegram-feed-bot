import os
from prometheus_client import start_http_server, Counter


def init_metrics():
    metrics_enabled = os.environ.get("ENABLE_METRICS")
    if metrics_enabled is not None and metrics_enabled.lower() == "true":
        start_http_server(
            addr=os.environ.get("METRICS_SERVER_HOST", "0.0.0.0"),
            port=int(os.environ.get("METRICS_SERVER_PORT", "8080")),
        )


MESSAGES_SENT = Counter("messages_sent", "Number of messages sent", ["status"])
MESSAGES_QUEUED = Counter("messages_queued", "Number of messages queued")
FEEDS_FETCHED = Counter("feeds_fetched", "Number of feeds fetched", ["status"])


def with_operation_counter(metric):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                metric.labels("ok").inc()
                return result
            except Exception as e:
                metric.labels("error").inc()
                raise e

        return wrapper

    return decorator
