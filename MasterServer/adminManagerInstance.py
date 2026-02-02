import asyncio
import singletonManager

from typing import Dict
from loggingSystem import LoggingSystem
from Models.device import Devices

class AdminManagerInstance:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AdminManagerInstance, cls).__new__(cls)
            cls._instance.init()
        return cls._instance
    
    def init(self):
        self.request_headers = {
            "Content-Type": "application/json"
        }

    async def updateNotificationDevices(self, request: Dict[str, Devices]):
        try:
            result = await singletonManager.DBManager().app_notification_info_db.updateNotificationDeviceList(request)
            if result:
                return {"code": "200", "success": True, "message": "Notification devices updated successfully."}
            
            return {"code": "400", "success": False, "message": "Failed to update notification devices."}
        except Exception as e:
            return {"code": "500", "success": False, "message": f"Error when updating notification devices: {str(e)}"}