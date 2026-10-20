import os

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me-in-production-32+")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30