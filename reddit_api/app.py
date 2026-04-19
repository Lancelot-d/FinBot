"""FastAPI application for the FinBot Reddit API service."""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc
import uvicorn

from scrapping import background_scrapping
from adapter import vector_db_adapter
from adapter import finbot_agent
from dao import DAO
from logger_config import logger

scheduler = AsyncIOScheduler(timezone=utc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the application lifespan, starting/stopping the scheduler.

    Args:
        fastapi_app: The FastAPI application instance.
    """
    logger.info("Starting application lifespan")
    logger.info("Running initial vector index build")
    vector_db_adapter.sync_new_posts()
    scheduler.start()
    logger.info("Scheduler started")
    yield
    logger.info("Shutting down scheduler")
    scheduler.shutdown()
    logger.info("Application lifespan shutdown complete")


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness endpoint for quick connectivity checks."""
    return {"status": "ok"}


@app.get("/complete_message/")
async def complete_message(input_string: str) -> dict[str, str]:
    """
    Example call:
    GET /complete_message/?input_string=Hello
    """
    start_time = time.time()
    try:
        logger.info("Received /complete_message request")
        response = finbot_agent.FinBotAgent().run(input_string)
        processing_time = time.time() - start_time
        logger.info("Request processed successfully in %.3f seconds", processing_time)
    except Exception:  # noqa: BLE001
        logger.exception("Error during chat invocation")
        return {"error": "Failed to process the request"}

    return {"completed_message": f"{response}"}


@app.get("/reddit_posts/count")
async def get_reddit_posts_count() -> dict[str, int] | dict[str, str]:
    """Return the number of reddit posts currently stored in the database."""
    try:
        logger.info("Received /reddit_posts/count request")
        count = DAO.get_instance().get_reddit_posts_count()
        return {"count": count}
    except (ValueError, RuntimeError):
        logger.exception("Error while counting reddit posts")
        return {"error": "Failed to fetch reddit post count"}


"""
# every 10 hours scrape new reddit posts and update vector index in the background

@scheduler.scheduled_job("interval", seconds=36000)
async def scrape_and_update_vector_db() -> None:
    logger.info("Background scraping job started")
    try:
        background_scrapping.run()
        vector_db_adapter.sync_new_posts()
        logger.info("Background scraping job completed successfully")
    except (ValueError, RuntimeError):
        logger.exception("Error during background scraping or vector index update")
"""

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
