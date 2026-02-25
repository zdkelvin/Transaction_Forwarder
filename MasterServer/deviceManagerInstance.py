import logging, httpx, asyncio
import singletonManager
import Utils.generalUtils as GeneralUtils

from loggingSystem import LoggingSystem
from Models.apiRequestData import UpdateDeviceData, AccountRegisterationData, NotificationData
from Models.device import Devices
from Utils.notificationUtils import getBankCodeByNotification, parseNotification, jsonableNotification

class DeviceManagerInstance:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DeviceManagerInstance, cls).__new__(cls)
            cls._instance.init()
        return cls._instance
    
    def init(self):
        self.request_headers = {
            "Content-Type": "application/json",
            "User-Agent": "GMPay/TransactionForwarder",
            "X-Signature": "",
            "X-Timestamp": "",
            "X-Device-ID": ""
        }
        self.is_production = singletonManager.DBManager().server_info_db.server_config.production_mode
        self.user = singletonManager.DBManager().server_info_db.server_config.user
        self.secret_key = singletonManager.DBManager().server_info_db.server_config.secret_key

    async def getDeviceData(self, request: UpdateDeviceData):
        try:
            device_data = singletonManager.DBManager().app_notification_info_db.getDeviceData(request.device_id)
            if device_data is None:
                return_data = {
                    "device_id": request.device_id,
                    "device_name": "",
                    "token": "",
                    "accounts": {}
                }
                LoggingSystem.apiLog(logging.INFO, f'Device data not found for device ID {request.device_id}. Returning empty data.')
                return {"code": "200", "success": True, "message": "Device data retrieved successfully.", "data": return_data}
            else:
                device: Devices
                register_accounts: dict
                device, register_accounts = device_data
                return_data = {
                    "device_id": request.device_id,
                    "device_name": device.name,
                    "token": device.token,
                    "accounts": register_accounts
                }
                LoggingSystem.apiLog(logging.INFO, f'Device data retrieved for device ID {request.device_id}: {return_data}')
                return {"code": "200", "success": True, "message": "Device data retrieved successfully.", "data": return_data}
        except Exception as e:
            LoggingSystem.apiLog(logging.ERROR, f'Error when retrieving device data for device ID {request.device_id}: {e}')
            return {"code": "500", "success": False, "message": f"Error when retrieving device data: {str(e)}"}
        
    async def bindDeviceAccounts(self, request: AccountRegisterationData):
        try:
            if singletonManager.DBManager().app_notification_info_db.checkDuplicateAccountBinding(
                request.app_name,
                request.account_number
            ):
                return {"code": "409", "success": False, "message": "Account already bound on other device."}
            
            update_result, device_data = await singletonManager.DBManager().app_notification_info_db.tryBindDeviceAccounts(
                request.device_id,
                request.device_name,
                request.app_name,
                request.account_number
            )

            if update_result == False:
                return {"code": "400", "success": False, "message": "Failed to bind notification device accounts."}
            
            sync_result = await self.syncDeviceConfig(request.device_id, device_data)
            if sync_result:
                result = await singletonManager.DBManager().app_notification_info_db.bindDeviceAccounts(
                    request.device_id,
                    request.device_name,
                    request.app_name,
                    request.account_number
                )

                if result:
                    return {"code": "200", "success": True, "message": "Notification device accounts bind successfully."}
            
            return {"code": "400", "success": False, "message": "Failed to bind notification device accounts."}
        except Exception as e:
            return {"code": "500", "success": False, "message": f"Error when binding notification device accounts: {str(e)}"}
        
    async def unbindDeviceAccounts(self, request: AccountRegisterationData):
        try:
            update_result, device_data = await singletonManager.DBManager().app_notification_info_db.tryUnbindDeviceAccounts(
                request.device_id,
                request.device_name,
                request.app_name,
                request.account_number
            )

            sync_result = await self.syncDeviceConfig(request.device_id, device_data)
            if sync_result:
                result = await singletonManager.DBManager().app_notification_info_db.unbindDeviceAccounts(
                    request.device_id,
                    request.device_name,
                    request.app_name,
                    request.account_number
                )

                if result:
                    return {"code": "200", "success": True, "message": "Notification device accounts unbound successfully."}
            
            return {"code": "404", "success": False, "message": "Failed to unbind notification device accounts."}
        except Exception as e:
            return {"code": "500", "success": False, "message": f"Error when unbinding notification device accounts: {str(e)}"}
        
    async def newNotificationPosted(self, request: NotificationData):
        try:
            LoggingSystem.apiLog(logging.INFO, f'New notification posted received: {request}')

            app_names = await singletonManager.DBManager().app_notification_info_db.getRegisterdAppNames()
            if request.app_name not in app_names:
                LoggingSystem.apiLog(logging.WARNING, f'App name {request.app_name} not found in registered app names.')
                return {"code": "404", "success": False, "message": "App name not found."}
            
            device_id = request.device_id
            device_name = request.device_name
            app_name = request.app_name
            bank_code = getBankCodeByNotification(app_name, request.title)
            notification_data = parseNotification(request.title, request.content, request.timestamp, bank_code)
            notification_data_json = jsonableNotification(notification_data) if notification_data else None
            if notification_data is None:
                LoggingSystem.apiLog(logging.WARNING, f'Failed to parse notification for app {app_name} with title: {request.title}')
                return {"code": "400", "success": False, "message": "Invalid notification."}
            
            domain = singletonManager.DBManager().server_info_db.getUserDomain(self.is_production)
            if domain is None:
                LoggingSystem.apiLog(logging.ERROR, 'Server domain is not configured properly.')
                return {"code": "500", "success": False, "message": "Error when forwarding notification."}
            
            date_time = GeneralUtils.getCurrentDT_String()
            date_time_unix = GeneralUtils.convertToTimestamp(date_time, '%d%m%Y_%H%M%S')
            url = f"{domain}create_transaction"
            payload_json = {
                "device_id": device_id,
                "device_name": device_name,
                "bank_code": bank_code,
                "notification_data": notification_data_json,
                "notification_content_original": request.content,
                "date_time": date_time
            }
            LoggingSystem.apiLog(logging.INFO, f"{payload_json}")
            signature = f"{device_id}{date_time}{self.secret_key}{bank_code}"
            hashed_signature = GeneralUtils.hashSignature(signature)
            LoggingSystem.apiLog(logging.INFO, f'Generated signature for new notification: {signature} : {hashed_signature}')
            request_headers = self.request_headers.copy()
            request_headers["X-Signature"] = hashed_signature
            request_headers["X-Timestamp"] = date_time_unix
            request_headers["X-BankCode"] = bank_code
            request_headers["X-DeviceID"] = device_id
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json = payload_json, headers = request_headers, timeout = 30)
                if response.status_code == 200:
                    LoggingSystem.apiLog(logging.INFO, f'Notification forwarded successfully to {url} for device ID {device_id}.')
                    return {"code": "200", "success": True, "message": "Notification forwarded successfully."}
                else:
                    LoggingSystem.apiLog(logging.ERROR, f'Failed to forward notification to {url} for device ID {device_id}. Response code: {response.status_code}')
                    return {"code": "400", "success": False, "message": "Failed to forward notification."}
        except Exception as e: 
            LoggingSystem.apiLog(logging.ERROR, f'Error when get task server for new notification posted: {e}')
            return {"code": "500", "success": False, "message": f"Error when get task server for new notification posted."}
        
    async def syncDeviceConfig(self, device_id: str, device_data: Devices):
        try:
            domain = singletonManager.DBManager().server_info_db.getUserDomain(self.is_production)
            if domain is None:
                LoggingSystem.apiLog(logging.ERROR, 'Server domain is not configured properly.')
                return

            date_time = GeneralUtils.getCurrentDT_String()
            date_time_unix = GeneralUtils.convertToTimestamp(date_time, '%d%m%Y_%H%M%S')
            url = f"{domain}bind_platform_bank_device"
            if device_data is None:
                payload_json = {
                    "device_id": device_id,
                    "device_name": "",
                    "accounts": {}
                }
            else:
                account_json = {}
                for app in device_data.apps:
                    account_json.setdefault(app.bank_code, []).extend(app.account_list)
                payload_json = {
                    "device_id": device_id,
                    "device_name": device_data.name,
                    "accounts": account_json
                }

            signature = f"{device_id}{self.secret_key}{date_time}"
            hashed_signature = GeneralUtils.hashSignature(signature)
            request_headers = self.request_headers.copy()
            request_headers["X-Signature"] = hashed_signature
            request_headers["X-Timestamp"] = date_time_unix
            request_headers["X-Device-ID"] = device_id
            LoggingSystem.apiLog(logging.INFO, f"Url: {url}")
            LoggingSystem.apiLog(logging.INFO, f'Syncing device config for device ID {device_id} with data: {payload_json}, headers: {request_headers}')
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json = payload_json, headers = request_headers, timeout = 30)
                LoggingSystem.apiLog(logging.INFO, f"Response Status Code: {response.status_code}")
                if response.status_code == 200:
                    LoggingSystem.apiLog(logging.INFO, f'Device config update notified successfully to {url} for device ID {device_id}.')
                    return True
                else:
                    LoggingSystem.apiLog(logging.ERROR, f'Failed to notify device config update to {url} for device ID {device_id}. Response code: {response.status_code}')
                    return False
        except Exception as e:
            LoggingSystem.apiLog(logging.ERROR, f'Error when notifying device config update for device ID {device_id}: {e}')
            return False
        
    async def deviceConfigUpdated(self, device_id: str):
        try:
            domain = singletonManager.DBManager().server_info_db.getUserDomain(self.is_production)
            if domain is None:
                LoggingSystem.apiLog(logging.ERROR, 'Server domain is not configured properly.')
                return
            
            device_data = singletonManager.DBManager().app_notification_info_db.getDeviceData(device_id)

            date_time = GeneralUtils.getCurrentDT_String()
            date_time_unix = GeneralUtils.convertToTimestamp(date_time, '%d%m%Y_%H%M%S')
            url = f"{domain}bind_platform_bank_device"
            if device_data is None:
                payload_json = {
                    "device_id": device_id,
                    "device_name": "",
                    "accounts": {}
                }
            else:
                device, account_list = device_data
                account_json = {}
                for app in device.apps:
                    account_json.setdefault(app.bank_code, []).extend(app.account_list)
                payload_json = {
                    "device_id": device_id,
                    "device_name": device.name,
                    "accounts": account_json
                }

            signature = f"{device_id}{self.secret_key}{date_time}"
            hashed_signature = GeneralUtils.hashSignature(signature)
            request_headers = self.request_headers.copy()
            request_headers["X-Signature"] = hashed_signature
            request_headers["X-Timestamp"] = date_time_unix
            request_headers["X-Device-ID"] = device_id
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json = payload_json, headers = request_headers, timeout = 30)
                if response.status_code == 200:
                    LoggingSystem.apiLog(logging.INFO, f'Device config update notified successfully to {url} for device ID {device_id}.')
                    return True
                else:
                    LoggingSystem.apiLog(logging.ERROR, f'Failed to notify device config update to {url} for device ID {device_id}. Response code: {response.status_code}')
                    return False
        except Exception as e:
            LoggingSystem.apiLog(logging.ERROR, f'Error when notifying device config update for device ID {device_id}: {e}')
            return False