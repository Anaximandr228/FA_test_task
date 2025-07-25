from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from enum import Enum
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

# Создаем базовый класс с использованием declarative_base()
Base = declarative_base()


class TaskStatus(Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'


# Создаем ENUM тип для PostgreSQL
task_status_enum = PgEnum(
    TaskStatus,
    name="task_status",
    create_type=True,
    values_callable=lambda obj: [e.value for e in obj]
)


# Создание модели для таблицы User
class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # Разрешаем переопределение

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)

    tasks = relationship("Task", back_populates="owner")


# Создание модели для таблицы Task
class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = {'extend_existing': True}  # Разрешаем переопределение

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    status = Column(
        task_status_enum,
        default=TaskStatus.PENDING.value,
        nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="tasks")
