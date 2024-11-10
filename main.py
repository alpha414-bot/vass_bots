from database import get_db
from utils.schemas import RawRequestData
from utils.settings import settings, emblem
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi import Depends, BackgroundTasks
from utils.views import start_prep_data


app = FastAPI()

# Add CORS middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.post("/quote/price")
def get_quote_price(
    data: RawRequestData,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    return start_prep_data(data=data, background_tasks=background_tasks, db=db)


if __name__ == "__main__":
    import uvicorn

    print(emblem)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8085,
        reload=True,
        access_log=True,
        reload_includes=["*.py", ".env"],
    )
