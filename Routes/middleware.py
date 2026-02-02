import logging
import singletonManager

from loggingSystem import LoggingSystem
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class VerifyAdminPairKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        admin_key = request.headers.get("X-ADMIN-KEY", "").strip()
        apis = [
            "/v1/updateDevice"
        ]

        if request.url.path in apis:
            if not admin_key:
                LoggingSystem.apiLog(logging.ERROR, "Admin key is required for this API.")
                return JSONResponse(
                    status_code = 401,
                    content = {
                        "code": "401",
                        "status": "Failed",
                        "result": False,
                        "message": "Unauthorized access without admin key.",
                        "data": None
                    }
                )
            else:
                if not singletonManager.DBManager().server_info_db.verifyAdminKey(admin_key):
                    LoggingSystem.apiLog(logging.ERROR, f"Unauthorized access with invalid admin key: {admin_key}")
                    return JSONResponse(
                        status_code = 401,
                        content = {
                            "code": "401",
                            "status": "Failed",
                            "result": False,
                            "message": "Unauthorized access with invalid admin key.",
                            "data": None
                        }
                    )
                else:
                    request.state.is_admin = True
        else:
            request.state.is_admin = True
        
        response = await call_next(request)
        return response

class VerifyAppPairKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        app_pair_key = request.headers.get("X-PAIR-KEY", "").strip()
        apis = [
            "/v1/getDeviceData",
            "/v1/addNotificationDevice",
            "/v1/removeNotificationDevice",
            "/v1/newNotificationPosted"
        ]

        if request.url.path in apis:
            if not app_pair_key:
                LoggingSystem.apiLog(logging.ERROR, "App pair key is required for this API.")
                return JSONResponse(
                    status_code = 401,
                    content = {
                        "code": "401",
                        "status": "Failed",
                        "result": False,
                        "message": "Unauthorized access without app pair key.",
                        "data": None
                    }
                )
            else:
                if not singletonManager.DBManager().server_info_db.verifyAppPairKey(app_pair_key):
                    LoggingSystem.apiLog(logging.ERROR, f"Unauthorized access with invalid app pair key: {app_pair_key}")
                    return JSONResponse(
                        status_code = 401,
                        content = {
                            "code": "401",
                            "status": "Failed",
                            "result": False,
                            "message": "Unauthorized access with invalid app pair key.",
                            "data": None
                        }
                    )
                else:
                    LoggingSystem.apiLog(logging.INFO, f"App pair key verified: {app_pair_key}")
                    request.state.app_pair_key = app_pair_key
        else:
            request.state.app_pair_key = None
        
        response = await call_next(request)
        return response