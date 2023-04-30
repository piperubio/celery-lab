from fastapi import FastAPI 
from fastapi.responses import JSONResponse

from tasks import celery_app, attach_drawings, sync_work_order


app = FastAPI()

@app.post("/sync", status_code=201)
def run_sync():
    task = sync_work_order.delay()
    return JSONResponse({"task_id": task.id})

@app.post("/attach-drawings", status_code=201)
def run_attach_drawings(wo_id: str):
    task = attach_drawings.delay(wo_id)
    return JSONResponse({"task_id": task.id})


@app.get("/tasks/{task_id}")
def get_status(task_id):
    task_result = celery_app.AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JSONResponse(result)