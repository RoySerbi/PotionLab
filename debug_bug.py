from sqlmodel import Session, create_engine, select
from app.models.user import User
from app.core.security import authenticate_user

engine = create_engine("sqlite:///:memory:")
User.metadata.create_all(engine)

with Session(engine) as session:
    admin = User(username="admin", hashed_password="pw", role="admin")
    session.add(admin)
    session.commit()
    
    # Simulate login
    user = authenticate_user(session, "admin", "admin123")  # This would fail pw check
