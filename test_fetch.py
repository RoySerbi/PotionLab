from sqlmodel import create_engine, Session, SQLModel, select
from sqlalchemy import text
from app.models.user import User

engine = create_engine("sqlite:///:memory:")
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    session.exec(text("INSERT INTO user (username, hashed_password, role) VALUES ('admin2', 'pw', 'admin')"))
    session.commit()
    
    user = session.exec(select(User).where(User.username == "admin2")).first()
    print(user.role)
