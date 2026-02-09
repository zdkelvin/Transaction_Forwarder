import singletonManager

from fastapi import APIRouter
from Routes.baseRoute import BaseResponseHandler
from Models.apiRequestData import UpdateDeviceData, AccountRegisterationData, NotificationData

router = APIRouter()

@router.post("/v1/getDeviceData")
async def getDeviceData(request: UpdateDeviceData):
    try:
        result = await singletonManager.DeviceManager().getDeviceData(request)
        return BaseResponseHandler.apiResponse(result)
    except Exception as e:
        return BaseResponseHandler.apiError("500", f"Error: {str(e)}")

@router.post("/v1/addNotificationDevice")
async def addNotificationDevice(request: AccountRegisterationData):
    try:
        result = await singletonManager.DeviceManager().bindDeviceAccounts(request)
        return BaseResponseHandler.apiResponse(result)
    except Exception as e:
        return BaseResponseHandler.apiError("500", f"Error: {str(e)}")
    
@router.post("/v1/removeNotificationDevice")
async def removeNotificationDevice(request: AccountRegisterationData):
    try:
        result = await singletonManager.DeviceManager().unbindDeviceAccounts(request)
        return BaseResponseHandler.apiResponse(result)
    except Exception as e:
        return BaseResponseHandler.apiError("500", f"Error: {str(e)}")
    
@router.post("/v1/newNotificationPosted")
async def newNotificationPosted(request: NotificationData):
    try:
        result = await singletonManager.DeviceManager().newNotificationPosted(request)
        return BaseResponseHandler.apiResponse(result)
    except Exception as e:
        return BaseResponseHandler.apiError("500", f"Error: {str(e)}")