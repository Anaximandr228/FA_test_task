from typing import Generator
import psycopg2
import pytest
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from starlette.testclient import TestClient
from app import models
from app.config import user, password, host
from app.fa_app import app, get_db

SQLALCHEMY_DATABASE_URL = f'postgresql://{user}:{password}@{host}/test'


@pytest.fixture(scope="session")
def connection():
    con = psycopg2.connect(dbname='postgres', user=user, host=host, password=password)
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    cur.execute('DROP DATABASE IF EXISTS test')
    cur.execute("CREATE DATABASE test")
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    models.Base.metadata.create_all(bind=engine)
    conn = engine.connect()
    yield conn
    conn.close()
    cur.close()
    con.close()


@pytest.fixture(scope="session")
def db_session(connection):
    transaction = connection.begin()
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = session_factory()
    yield session
    session.close()
    transaction.rollback()


@pytest.fixture(scope="function")
def client(db_session) -> Generator:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def tasks_setup(db_session: Session):
    db_user = models.User(username='testuser', password='adminadmin')
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    db_task = models.Task(
        title='Создание программы',
        description='Разработать программу в соответствии с ТЗ',
        status='done',
        owner_id=db_user.id
    )
    db_session.add(db_task)
    db_session.commit()
    db_session.refresh(db_task)
    yield db_user, db_task
    # Очистка
    db_session.query(models.Task).delete()
    db_session.query(models.User).delete()
    db_session.commit()

print([route.path for route in app.routes])

def test_post_user(client, db_session):
    data = {
        "username": "AdminTest",
        "password": "11111",
    }
    response = client.post("/register", json=data)
    assert response.status_code == 200
    assert response.json()['username'] == 'AdminTest'
    user_in_db = db_session.query(models.User).filter(models.User.username == "AdminTest").first()
    assert user_in_db is not None
    assert user_in_db.username == 'AdminTest'


def test_get_tasks_list(client, tasks_setup):
    _, db_task = tasks_setup
    response = client.get("/tasks/?status=done")
    assert response.status_code == 200
    result = response.json()
    assert any(task['title'] == db_task.title for task in result)


def test_post_task(client, tasks_setup, db_session):
    db_user, _ = tasks_setup
    data = {
        "title": "Создать тесты",
        "description": "Сделать тесты для API-эндпоинтов",
        "status": "in_progress",
        "owner_id": db_user.id
    }
    response = client.post("/tasks/", json=data)
    assert response.status_code == 200
    assert response.json()['title'] == 'Создать тесты'
    saved_task = db_session.query(models.Task).filter(models.Task.title == "Создать тесты").first()
    assert saved_task is not None
    assert saved_task.title == 'Создать тесты'


def test_post_update_task(client, tasks_setup, db_session):
    db_user, db_task = tasks_setup
    data = {
        "id": db_task.id,
        "title": db_task.title,
        "description": db_task.description,
        "status": "done",
        "owner_id": db_user.id
    }
    response = client.put("/tasks/", json=data)
    assert response.status_code == 200
    assert response.json()['status'] == "done"
    updated_task = db_session.query(models.Task).filter(models.Task.id == db_task.id).first()
    assert updated_task.status == "done"


def test_delete_task(client, tasks_setup, db_session):
    _, db_task = tasks_setup
    response = client.delete(f"/tasks/{db_task.id}")
    assert response.status_code == 200
    assert response.json()['message'] == 'Данные были удалены'
    task = db_session.query(models.Task).filter(models.Task.id == db_task.id).first()
    assert task is None
