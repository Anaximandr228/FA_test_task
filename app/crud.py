from typing import Optional
from sqlalchemy.orm import Session
import models
from shemas import UserCreate, TaskCreate
from passlib.hash import argon2


def create_user(db: Session, user: UserCreate):
    hashed_password = argon2.hash(user.password)
    db_user = models.User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def verify_password(plain_password, hashed_password):
    return argon2.verify(plain_password, hashed_password)


# Task CRUD operations
def create_task(db: Session, task: dict, user_id: int):
    # Преобразуем строковый статус в ENUM значение
    if 'status' in task and isinstance(task['status'], str):
        task['status'] = models.TaskStatus(task['status']).value

    db_task = models.Task(**task, owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_tasks(db: Session, user_id: int, status: Optional[str] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Task).filter(models.Task.owner_id == user_id)

    if status:
        status_enum = models.TaskStatus(status)
        query = query.filter(models.Task.status == status_enum.value)

    return query.offset(skip).limit(limit).all()


def get_task(db: Session, task_id: int, user_id: int):
    return db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == user_id
    ).first()


def update_task(db: Session, db_task: models.Task, update_data: dict):
    for key, value in update_data.items():
        # Преобразуем строковый статус в ENUM значение
        if key == 'status' and isinstance(value, str):
            value = models.TaskStatus(value).value
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int, user_id: int):
    task = get_task(db, task_id, user_id)
    if task:
        db.delete(task)
        db.commit()
        return {"message": "Данные были удалены"}
