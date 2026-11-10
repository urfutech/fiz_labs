from typing import Annotated

from fastapi import FastAPI, Depends, Query, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select
import psycopg2
from psycopg2.extras import RealDictCursor


class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    secret_name: str


class HeroPublic(HeroBase):
    id: int


class HeroCreate(HeroBase):
    secret_name: str


class HeroUpdate(HeroBase):
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None


try:
    conn = psycopg2.connect(
        host="localhost",
        databse="name",
        user="postgres",
        password="pass",
        cursor_factory=RealDictCursor,
    )
    cursor = conn.cursor()
    print("Database connection success")
except Exception as error:
    print("Connect to database failed")
    print("Error: ", error)


@app.post("/labs/{lab_id}")
def enter_answer(row: int, answer: string):
    cursor.execute(
        """"INSERT INTO labs (row, answer) VALUES (%s, %s)
        RETURNING *""",
        (row, answer),
    )
    new_lab = cursor.fetchone()
    conn.comit()


@app.delete("/labs/{lab_id}")
def delete_lab(lab_id: int):
    cursor.execute("""DELETE FROM labs WHERE lab_id = %s RETURNING""", (lab_id))
    deleted_lab = cursor.fetchone()
    conn.comit()

    if deleted_lab == None:
        raise HTTPException(status_code=404)
    return Response(status_code=200)


@app.put("/labs/{lab_id}")
def update_lab(lab_id: int, mess: str):
    cursor.execute("""""")


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/heroes/", response_model=HeroPublic)
def create_hero(hero: HeroCreate, session: SessionDep):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@app.get("/heroes/", response_model=HeroPublic)
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes


@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero: HeroUpdate, session: SessionDep):
    hero_db = session.get(Hero, hero_id)
    if not hero_id:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero.model_dump(exclude_unset=True)
    hero_db.sqlmodel_update(hero_data)
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)
    return hero_db


@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}
