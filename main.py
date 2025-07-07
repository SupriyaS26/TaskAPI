from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()
DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# SQLAlchemy model
class TaskModel(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)


# Pydantic schema
class TaskCreate(BaseModel):
    title: str
    description: str
    is_completed: Optional[bool] = False


class Task(TaskCreate):
    id: int

    class Config:
        orm_mode = True


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# POST /tasks
@app.post("/tasks", response_model=Task)
def create_task(task: TaskCreate):
    db = next(get_db())
    db_task = TaskModel(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


# GET /tasks
@app.get("/tasks", response_model=List[Task])
def get_tasks(is_completed: Optional[bool] = Query(None)):
    db = next(get_db())
    if is_completed is not None:
        return db.query(TaskModel).filter(TaskModel.is_completed == is_completed).all()
    return db.query(TaskModel).all()


# GET /tasks/{id}
@app.get("/tasks/{id}", response_model=Task)
def get_task(id: int):
    db = next(get_db())
    task = db.query(TaskModel).filter(TaskModel.id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# PUT /tasks/{id}
@app.put("/tasks/{id}", response_model=Task)
def update_task(id: int, updated_task: TaskCreate):
    db = next(get_db())
    task = db.query(TaskModel).filter(TaskModel.id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in updated_task.dict().items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


# DELETE /tasks/{id}
@app.delete("/tasks/{id}")
def delete_task(id: int):
    db = next(get_db())
    task = db.query(TaskModel).filter(TaskModel.id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted"}
