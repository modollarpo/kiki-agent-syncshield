import redis
import uuid
import json
import os
from fastapi import APIRouter, BackgroundTasks
from services.synccreate.logic.prompt_engineer import MultimediaPromptEngineer

VIDEO_QUEUE = os.getenv("VIDEO_QUEUE", "video_jobs")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

router = APIRouter()
prompt_engineer = MultimediaPromptEngineer()

r = redis.Redis.from_url(REDIS_URL)

@router.post("/generate_video")
def generate_video(request: dict, background_tasks: BackgroundTasks):
    """
    Accepts: {audience_segment, product_desc, user_id}
    Returns: {job_id}
    """
    job_id = str(uuid.uuid4())
    prompt = prompt_engineer.craft_video_prompt(request.get("audience_segment", "default"), request.get("product_desc", ""))
    job = {
        "job_id": job_id,
        "prompt": prompt,
        "user_id": request.get("user_id"),
        "status": "queued"
    }
    r.lpush(VIDEO_QUEUE, json.dumps(job))
    return {"job_id": job_id, "status": "queued"}

@router.get("/video_status/{job_id}")
def video_status(job_id: str):
    # For demo: just return status from Redis (in production, use a DB or more robust tracking)
    status = r.get(f"video_status:{job_id}")
    if status:
        return json.loads(status)
    return {"job_id": job_id, "status": "unknown"}

@router.get("/video_url/{job_id}")
def video_url(job_id: str):
    url = r.get(f"video_url:{job_id}")
    if url:
        return {"job_id": job_id, "url": url.decode()}
    return {"job_id": job_id, "url": None}
