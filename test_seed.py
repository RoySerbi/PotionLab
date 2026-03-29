from sqlmodel import create_engine, Session, SQLModel, select
from app.models.user import User
from scripts.seed import seed_admin_user

engine = create_engine("sqlite:///:memory:")
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    seed_admin_user(session)
    admin = session.exec(select(User).where(User.username == "admin")).first()
    print(f"Role in DB: {admin.role}")
