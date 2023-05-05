from datetime import datetime, timedelta

from fastapi import HTTPException, Request

from core.settings import settings

RATE_LIMITS = {}
LIMIT = settings.limit
TIME_WINDOW = timedelta(seconds=settings.time_window)


def rate_limiter(request: Request):
    ip_address = request.client.host
    if ip_address not in RATE_LIMITS:
        RATE_LIMITS[ip_address] = {"count": 0, "start_time": datetime.now()}
    if (
        RATE_LIMITS[ip_address]["count"] >= LIMIT
        and datetime.now() - RATE_LIMITS[ip_address]["start_time"]
        <= TIME_WINDOW
    ):
        raise HTTPException(status_code=429, detail="Too Many Requests")
    RATE_LIMITS[ip_address]["count"] += 1
    if datetime.now() - RATE_LIMITS[ip_address]["start_time"] > TIME_WINDOW:
        RATE_LIMITS[ip_address] = {"count": 1, "start_time": datetime.now()}
    return True
