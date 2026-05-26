import os

LOCAL_FRONTEND_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]


def get_env_value(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)

    if value is None:
        return default

    normalized = value.strip().strip('"').strip("'")

    if normalized.lower() in {"", "null", "none", "undefined"}:
        return default

    return normalized


def get_cors_origins() -> list[str]:
    raw_origins = get_env_value("CORS_ORIGINS")
    frontend_url = get_env_value("FRONTEND_URL")

    if raw_origins:
        origins = [origin.strip().rstrip("/") for origin in raw_origins.split(",")]
        return [origin for origin in origins if origin]

    if frontend_url:
        return [frontend_url.rstrip("/")]

    return LOCAL_FRONTEND_ORIGINS
