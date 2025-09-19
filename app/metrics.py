from prometheus_client import Counter, Histogram

REQUESTS_TOTAL = Counter("requests_total", "Total /process requests")
REQUEST_DURATION = Histogram("request_duration_seconds", "Time taken for process endpoint")
AGENT_ERRORS = Counter("agent_errors_total", "Count of agent failures/timeouts")