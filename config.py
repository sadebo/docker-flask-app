import os

class Config:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    APP_NAME = os.getenv("APP_NAME", "Flask CRUD API")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data.db")

    # --- Redis connection handling ---
    REDIS_URL = os.getenv("REDIS_URL")
    if REDIS_URL:
        # Accept URLs like tcp://10.0.55.55:6379 or redis://hostname:6379
        stripped = REDIS_URL.replace("tcp://", "").replace("redis://", "")
        parts = stripped.split(":")
        REDIS_HOST = parts[0]
        try:
            REDIS_PORT = int(parts[1]) if len(parts) > 1 else 6379
        except ValueError:
            REDIS_PORT = 6379
    else:
        REDIS_HOST = os.getenv("REDIS_HOST", "redis.default.svc.cluster.local")
        REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
