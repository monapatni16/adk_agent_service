import structlog
import logging

def configure_logging(level: str = "INFO"):
    logging.basicConfig(format="%(message)s", level=getattr(logging, level.upper(), logging.INFO))
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.stdlib.LoggerFactory()
    )
    logger = structlog.get_logger().bind(service="adk_three_agent")
    return logger

logger = configure_logging()