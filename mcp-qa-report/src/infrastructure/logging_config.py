"""
Central logging configuration.

Routes logs to stderr (never stdout) to avoid breaking MCP stdio JSON-RPC.
LOG_LEVEL can override the default verbosity.
"""
import os
import logging
import sys

def configure_logging(level: int | None = None) -> None:
    if level is None:
        name = os.getenv("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, name, logging.INFO)

    logging.basicConfig(
        level=level,
        stream=sys.stderr,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=True,
    )
