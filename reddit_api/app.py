from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc
import uvicorn
from scrapping import background_scrapping
from adapter import faiss_adapter
from adapter import finbot_agent

scheduler = AsyncIOScheduler(timezone=utc)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting lifespan")
    faiss_adapter.batch_insert()
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/complete_message/")
async def complete_message(input_string: str):
    """
    Example call:
    GET /complete_message/?input_string=Hello
    """
    try:
        response = finbot_agent.FinBotAgent().run(input_string)
    except Exception as e:
        print(f"Error during chat invocation: {e}")
        return {"error": "Failed to process the request"}
    
    return {"completed_message": f"{response}"}

# every 10 hours
@scheduler.scheduled_job('interval', seconds=36000)
async def scrappe_and_update_faiss():
    print("Background scrapping started")
    try:
        background_scrapping.run()
        faiss_adapter.batch_insert()
    except Exception as e:
        print(f"Error during background scrapping or FAISS update : {e}")
    

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8080)
    
