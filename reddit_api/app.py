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
    except (ValueError, RuntimeError):
        logger.exception("Error during chat invocation")
        return {"error": "Failed to process the request"}

    return {"completed_message": f"{response}"}


# every 10 hours
@scheduler.scheduled_job("interval", seconds=36000)
async def scrape_and_update_vector_db() -> None:
    """Background job to scrape Reddit data and incrementally update vector DB."""
    logger.info("Background scraping job started")
    try:
        background_scrapping.run()
        vector_db_adapter.sync_new_posts()
        logger.info("Background scraping job completed successfully")
    except (ValueError, RuntimeError):
        logger.exception("Error during background scraping or vector index update")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
