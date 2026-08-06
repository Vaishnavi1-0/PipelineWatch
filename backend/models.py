from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
from datetime import datetime

class Failure(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    repo: str
    run_id: int
    workflow_name: str
    run_url: str
    summary: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

engine = create_engine("sqlite:///pipelinewatch.db")

def init_db():
    SQLModel.metadata.create_all(engine)

def save_failure(**kwargs):
    with Session(engine) as session:
        failure = Failure(**kwargs)
        session.add(failure)
        session.commit()

def get_failures():
    with Session(engine) as session:
        return session.exec(select(Failure).order_by(Failure.created_at.desc())).all()
