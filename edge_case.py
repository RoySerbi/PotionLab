from sqlmodel import Field, SQLModel, Session, create_engine, select
from sqlalchemy import Column, String

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column(String(80), unique=True, nullable=False))
    role: str = Field(default="reader", sa_column=Column(String(20), nullable=False))

engine = create_engine("sqlite:///:memory:")
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    user = User(username="admin", role="admin")
    session.add(user)
    session.commit()
    
    # Try fetching
    u = session.exec(select(User).where(User.username == "admin")).first()
    print("Fetched role:", u.role)
