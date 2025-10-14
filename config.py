import os

class Config:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    REDIS_HOST = os.getenv("REDIS_HOST", "redis.default.svc.cluster.local")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data.db")
    APP_NAME = os.getenv("APP_NAME", "Flask CRUD API")
