from sqlmodel import create_engine, Session, SQLModel
from app.models.user import User

engine = create_engine("sqlite:///:memory:")
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    admin = User(username="admin", hashed_password="pw", role="admin")
    session.add(admin)
    session.commit()
    session.refresh(admin)
    print(f"Role in DB: {admin.role}")
