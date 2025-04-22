from fastapi import FastAPI
from starlette import status
from starlette.responses import JSONResponse

from app.core.errors import register_all_errors
from app.main_router import main_router

app = FastAPI()

register_all_errors(app)
app.include_router(main_router)


@app.get("/")
async def root():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"currently server is running"})
