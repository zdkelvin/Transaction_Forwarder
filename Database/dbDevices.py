import json, logging, aiofiles
import Utils.generalUtils as GeneralUtils

from typing import Dict, List, Optional, Tuple
from loggingSystem import LoggingSystem
from Models.device import Devices, App
from Utils.notificationUtils import getBankCodeByAppName, getBankExternalAppName

class DBDevicesInfo:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBDevicesInfo, cls).__new__(cls)
            cls._instance.loadDevices()
        return cls._instance

    def loadDevices(self):
        try:
            with open(GeneralUtils.getPath("Assets/devices.json")) as file:
                data = json.loads(file.read())
                self.register_devices = {}
                for key, value in data.items():
                    self.register_devices[key] = Devices(**value)
        except:
            self.devices = None
            LoggingSystem.serverLog(logging.ERROR, 'Load app notification devices json failed.')

    async def refreshNotificationDevices(self):
        try:
            async with aiofiles.open(GeneralUtils.getPath("Assets/devices.json"), mode='r') as file:
                data = await file.read()
                parsed_data = json.loads(data)
                self.register_devices = {}
                for key, value in parsed_data.items():
                    self.register_devices[key] = Devices(**value)

                return {"code": "200", "success": True, "message": "Notification device list update successfully."}
        except:
            return {"code": "500", "success": True, "message": "Notification device list update failed."}

    async def bindDeviceAccounts(self, device_id: str, device_name: str, app_name: str, account: str):
        try:
            if device_id not in self.register_devices:
                self.register_devices[device_id] = Devices(apps=[])
            
            bank_code = getBankCodeByAppName(app_name)
            if bank_code is None:
                LoggingSystem.serverLog(logging.ERROR, f"Invalid app name: {app_name} for device to bind accounts: {device_id}.")
                return False
            
            device: Devices = self.register_devices[device_id]
            device.name = device_name
            app = next((app for app in device.apps if app.app_name == app_name), None)
            if app is None:
                external_app_name = getBankExternalAppName(bank_code)
                app = App(bank_code = bank_code, app_name = app_name, external_app_name = external_app_name, account_list = [account])
                device.apps.append(app)
            else:
                if account not in app.account_list:
                    app.account_list.append(account)

            save_data = {register_device_id: register_app.dict() for register_device_id, register_app in self.register_devices.items()}
            async with aiofiles.open(GeneralUtils.getPath("Assets/devices.json"), 'w') as file:
                await file.write(json.dumps(save_data, indent=4))

            LoggingSystem.serverLog(logging.INFO, f"Notification device {device_id} for app {app_name} accounts bound successfully.")
            return True
        except Exception as e:
            LoggingSystem.serverLog(logging.ERROR, f"Failed to bind accounts to notification device: {str(e)}")
            return False
        
    async def unbindDeviceAccounts(self, device_id: str, device_name: str, app_name: str, account: str):
        try:
            if device_id not in self.register_devices:
                LoggingSystem.serverLog(logging.ERROR, f"Device ID {device_id} not found in notification devices.")
                return False
            
            device: Devices = self.register_devices[device_id]
            app = next((app for app in device.apps if app.app_name == app_name), None)
            if app:
                if account in app.account_list:
                    app.account_list.remove(account)

                if len(app.account_list) == 0:
                    device.apps.remove(app)

            save_data = {register_device_id: register_app.dict() for register_device_id, register_app in self.register_devices.items()}
            async with aiofiles.open(GeneralUtils.getPath("Assets/devices.json"), 'w') as file:
                await file.write(json.dumps(save_data, indent=4))

            LoggingSystem.serverLog(logging.INFO, f"Notification device {device_id} for app {app_name} accounts unbound successfully.")
            return True
        except Exception as e:
            LoggingSystem.serverLog(logging.ERROR, f"Failed to unbind accounts from notification device: {str(e)}")
            return False
        
    async def updateDevice(self, device_id: str, device_name: str, device_token: str):
        try:
            if device_id not in self.register_devices:
                self.register_devices[device_id] = Devices(apps=[])
            
            device: Devices = self.register_devices[device_id]
            device.name = device_name
            device.token = device_token

            save_data = {register_device_id: register_app.dict() for register_device_id, register_app in self.register_devices.items()}
            async with aiofiles.open(GeneralUtils.getPath("Assets/devices.json"), 'w') as file:
                await file.write(json.dumps(save_data, indent = 4))

            LoggingSystem.serverLog(logging.INFO, f"Notification device {device_id} updated successfully.")
            return True
        except Exception as e:
            LoggingSystem.serverLog(logging.ERROR, f"Failed to update notification device: {str(e)}")
            return False
        
    async def updateNotificationDeviceList(self, device_list: Dict[str, Devices]):
        try:
            self.register_devices = device_list
            save_data = {register_device_id: register_app.dict() for register_device_id, register_app in self.register_devices.items()}
            async with aiofiles.open(GeneralUtils.getPath("Assets/devices.json"), 'w') as file:
                await file.write(json.dumps(save_data, indent = 4))

            LoggingSystem.serverLog(logging.INFO, f"Notification device list updated successfully.")
            return True
        except Exception as e:
            LoggingSystem.serverLog(logging.ERROR, f"Failed to update notification device list: {str(e)}")
            return False
        
    def getDeviceData(self, device_id: str) -> Optional[Tuple[Devices, Dict[str, List]]]:
        if device_id in self.register_devices:
            device: Devices = self.register_devices[device_id]
            account_list = {}
            for app in device.apps:
                account_list[app.app_name] = app.account_list
            return (device, account_list)
        
        return None
        
    def getNotificationDeviceByAccount(self, bank_code, account_number):
        for device_id, device_data in self.register_devices.items():
            for app in device_data.apps:
                if app.bank_code != bank_code:
                    continue

                if account_number in app.account_list:
                    return {
                        "device_id": device_id,
                        "app_name" : app.app_name,
                        "external_app_name": app.external_app_name,
                    }
                
        return None
    
    async def getRegisterdAppNames(self):
        try:
            app_names = []
            for device_id, device_data in self.register_devices.items():
                for app in device_data.apps:
                    if app.bank_code == "Maribank":
                        if app.external_app_name:
                            app_names.append(app.external_app_name)
                        else:
                            app_names.append(app.app_name)
                    else:
                        if app.app_name not in app_names:
                            app_names.append(app.app_name)
                        if app.external_app_name and app.external_app_name not in app_names:
                            app_names.append(app.external_app_name)
            return app_names
        except:
            return []
        
    def getAccountListByDeviceAppName(self, device_id, app_name):
        if device_id in self.register_devices:
            device: Devices = self.register_devices[device_id]
            app = next((app for app in device.apps if app.app_name == app_name), None)
            if app:
                return app.account_list
        return []
    
    def getAccountListByDevice(self, device_id):
        if device_id in self.register_devices:
            device: Devices = self.register_devices[device_id]
            account_list = {}
            for app in device.apps:
                account_list[app.app_name] = app.account_list
            
            return account_list
        return {}
    
    def checkDuplicateAccountBinding(self, app_name, account_number):
        bank_code = getBankCodeByAppName(app_name)
        if bank_code is None:
            return False
        
        for device_id, device_data in self.register_devices.items():
            for app in device_data.apps:
                if app.bank_code != bank_code:
                    continue

                if account_number in app.account_list:
                    return True
                
        return False