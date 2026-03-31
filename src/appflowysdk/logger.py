"""Structured logging for the AppFlowy SDK."""

from __future__ import annotations

import logging

logger = logging.getLogger("appflowysdk")

if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    )
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)
