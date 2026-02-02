import singletonManager

from typing import Dict
from fastapi import APIRouter, Request
from Routes.baseRoute import BaseResponseHandler
from Models.device import Devices

router = APIRouter()

@router.post("/v1/updateDevice")
async def updateDevice(request: Request, request_data: Dict[str, Devices] = {}):
    try:
        if not getattr(request.state, 'is_admin', False):
            return BaseResponseHandler.apiError("403", "Admin access required.")
        
        result = await singletonManager.AdminManager().updateNotificationDevices(request_data)
        return BaseResponseHandler.apiResponse(result)
    except Exception as e:
        return BaseResponseHandler.apiError("500", f"Error: {str(e)}")