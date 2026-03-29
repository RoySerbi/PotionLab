from sqlmodel import Session, select, create_engine
from app.models import User
engine = create_engine("sqlite:///data/app.db")
with Session(engine) as session:
    admin = session.exec(select(User).where(User.username == "admin")).first()
    print(f"DB says admin role is: {admin.role}")
