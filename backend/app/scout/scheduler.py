import asyncio
import logging
import os

from app.scout.scout_engine import ScoutEngine

logger = logging.getLogger(__name__)


class ScoutScheduler:
    def __init__(self):
        self.engine = ScoutEngine()
        self.interval_seconds = int(
            os.getenv("SCOUT_INTERVAL_SECONDS", "1800")
        )
        self.enabled = (
            os.getenv("SCOUT_SCHEDULER_ENABLED", "false").lower() == "true"
        )

    async def run_forever(self):
        if not self.enabled:
            logger.info("Scout scheduler is disabled.")
            return

        logger.info(
            "Scout scheduler started. Interval: %s seconds",
            self.interval_seconds,
        )

        while True:
            try:
                logger.info("Scout import started")

                results = self.engine.run()

                logger.info("Scout import finished: %s", results)

            except Exception:
                logger.exception("Scout import failed")

            await asyncio.sleep(self.interval_seconds)
