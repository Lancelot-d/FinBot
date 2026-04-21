"""FastAPI application for the FinBot Reddit API service."""

import asyncio
import concurrent.futures
import os
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
EXTRACTION_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
EXTRACTION_WORKERS = 4
EXTRACTION_BATCH_SIZE = int(os.getenv("EXTRACTION_BATCH_SIZE", "20"))


def _extract_and_store(
    post_id: str, content_str: str, agent: finbot_agent.FinBotAgent
) -> bool:
    """Extract facts from content and persist into extracted_information."""
    if not content_str.strip():
        return False

    extracted = agent.extract_finance_facts(content_str)
    if not extracted:
        return False

    return DAO.get_instance().update_reddit_post_extracted_information(
        post_id, extracted
    )


def _run_extraction_batch() -> int:
    """Process one batch of rows where extracted_information is null."""
    dao = DAO.get_instance()
    rows = dao.get_reddit_posts_missing_extracted_information(
        limit=EXTRACTION_BATCH_SIZE
    )
    if not rows:
        return 0

    agent = finbot_agent.FinBotAgent(model=EXTRACTION_MODEL, temperature=0.0)
    updated_count = 0
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=EXTRACTION_WORKERS
    ) as executor:
        futures = [
            executor.submit(_extract_and_store, post_id, content_str, agent)
            for post_id, content_str in rows
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                if future.result():
                    updated_count += 1
            except Exception:  # noqa: BLE001
                logger.exception("One row failed during extracted_information job")

    return updated_count


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


@scheduler.scheduled_job("interval", seconds=120, max_instances=1, coalesce=True)
async def backfill_extracted_information() -> None:
    """Background job to fill extracted_information for rows where it is null."""
    logger.info("Background extracted_information job started")
    try:
        updated_count = await asyncio.to_thread(_run_extraction_batch)
        logger.info(
            "Background extracted_information job completed: updated=%d",
            updated_count,
        )
    except Exception:  # noqa: BLE001
        logger.exception("Error during extracted_information background job")


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
