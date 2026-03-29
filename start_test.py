import subprocess
import time
import requests
from app.core.config import settings
from jose import jwt

def test():
    # Delete DB
    subprocess.run(["rm", "-f", "data/app.db"])
    
    # Run seed
    subprocess.run(["uv", "run", "python", "scripts/seed.py"])
    
    # Start app
    p = subprocess.Popen(["uv", "run", "uvicorn", "app.main:app", "--port", "8000"])
    time.sleep(2)
    
    try:
        # Login
        r = requests.post("http://localhost:8000/api/v1/auth/token", json={"username": "admin", "password": "admin123"})
        token = r.json()["access_token"]
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        print(f"Payload role: {payload.get('role')}")
    finally:
        p.terminate()
        p.wait()

test()
