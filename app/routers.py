from typing import Annotated, Optional, List
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app import models, crud
from app.shemas import UserCreate, TaskCreate, TaskUpdate, Task as TaskSchema
from app.database import engine, SessionLocal
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# Создаем таблицы
models.Base.metadata.create_all(bind=engine)

security = HTTPBasic()
app = FastAPI(
    title="Task Manager API",
    description="Simple REST API for task management with authentication",
    version="1.0.0"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_id(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)],
        db: Session = Depends(get_db)
) -> int:
    user = crud.get_user_by_username(db, credentials.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    # Используем новую функцию проверки пароля
    if not crud.verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return user.id


# Регистрация пользователя
@app.post("/register", response_model=UserCreate)
def register_user(
        user: UserCreate,
        db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


# Операции с задачами
@app.post("/tasks/", response_model=TaskSchema)
def create_task(
        task: TaskCreate,
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user_id)
):
    return crud.create_task(db, task.dict(), user_id)


@app.get("/tasks/", response_model=List[TaskSchema])
def read_tasks(
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user_id)
):
    return crud.get_tasks(db, user_id, status=status, skip=skip, limit=limit)


@app.put("/tasks/{task_id}", response_model=TaskSchema)
def update_task(
        task_id: int,
        task: TaskUpdate,
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user_id)
):
    db_task = crud.get_task(db, task_id, user_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.update_task(db, db_task, task.dict(exclude_unset=True))


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
        task_id: int,
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user_id)
):
    if not crud.delete_task(db, task_id, user_id):
        raise HTTPException(status_code=404, detail="Task not found")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)