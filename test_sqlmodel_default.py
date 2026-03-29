from sqlmodel import create_engine, Session, SQLModel, Field, select
from sqlalchemy import Column, String, text

class TestUser(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column(String(80), unique=True, nullable=False))
    role: str = Field(default="reader", sa_column=Column(String(20), nullable=False))

engine = create_engine("sqlite:///:memory:")
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    # Insert via SQL to bypass model default logic
    session.exec(text("INSERT INTO testuser (username, role) VALUES ('admin', 'admin')"))
    session.commit()
    
    user = session.exec(select(TestUser).where(TestUser.username == "admin")).first()
    print(f"Role from DB: {user.role}")
