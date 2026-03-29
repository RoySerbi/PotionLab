from app.models.user import User

u = User(username="admin", hashed_password="pw", role="admin")
print(u.role)
print(u.model_dump())
