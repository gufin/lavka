from datetime import datetime, timedelta

from fastapi import HTTPException, Request

from core.settings import settings

LIMIT = settings.limit
TIME_WINDOW = timedelta(seconds=settings.time_window)
rate_limits = {}


def rate_limiter(request: Request):
    ip_address = request.client.host
    if ip_address not in rate_limits:
        rate_limits[ip_address] = {"count": 0, "start_time": datetime.now()}
    if (
        rate_limits[ip_address]["count"] >= LIMIT
        and datetime.now() - rate_limits[ip_address]["start_time"]
        <= TIME_WINDOW
    ):
        raise HTTPException(status_code=429, detail="Too Many Requests")
    rate_limits[ip_address]["count"] += 1
    if datetime.now() - rate_limits[ip_address]["start_time"] > TIME_WINDOW:
        rate_limits[ip_address] = {"count": 1, "start_time": datetime.now()}
    return True
