from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from . import auth
from . import tracing
from . import logging
from sqlmodel import SQLModel, Session, create_engine
from . import models
from .database import engine
from starlette_prometheus import metrics

app = FastAPI()
app.add_route("/metrics", metrics)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    tracing.setup_tracing(app)
    logging.setup_logging()

def get_session():
    with Session(engine) as session:
        yield session

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # In a real application, you would verify the username and password against a database
    if form_data.username != "testuser" or form_data.password != "testpass":
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/strategies/", response_model=models.Strategy)
def create_strategy(strategy: models.Strategy, session: Session = Depends(get_session), current_user: str = Depends(auth.get_current_user)):
    session.add(strategy)
    session.commit()
    session.refresh(strategy)
    return strategy

@app.get("/strategies/", response_model=list[models.Strategy])
def read_strategies(session: Session = Depends(get_session)):
    strategies = session.query(models.Strategy).all()
    return strategies

@app.get("/strategies/{strategy_id}", response_model=models.Strategy)
def read_strategy(strategy_id: int, session: Session = Depends(get_session)):
    strategy = session.get(models.Strategy, strategy_id)
    return strategy

@app.put("/strategies/{strategy_id}", response_model=models.Strategy)
def update_strategy(strategy_id: int, strategy: models.Strategy, session: Session = Depends(get_session)):
    db_strategy = session.get(models.Strategy, strategy_id)
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    strategy_data = strategy.dict(exclude_unset=True)
    for key, value in strategy_data.items():
        setattr(db_strategy, key, value)
    session.add(db_strategy)
    session.commit()
    session.refresh(db_strategy)
    return db_strategy

from .celery_worker import run_backtest
from fastapi import WebSocket

@app.post("/runs/", response_model=models.Run)
def create_run(run: models.Run, session: Session = Depends(get_session)):
    session.add(run)
    session.commit()
    session.refresh(run)
    run_backtest.delay(run.strategy_id, run.bundle_id, str(run.start_date), str(run.end_date), run.capital_base)
    return run

@app.websocket("/ws/runs/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: int):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

@app.delete("/strategies/{strategy_id}")
def delete_strategy(strategy_id: int, session: Session = Depends(get_session)):
    strategy = session.get(models.Strategy, strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    session.delete(strategy)
    session.commit()
    return {"ok": True}
