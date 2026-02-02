import threading

db_manager_instance = None
admin_manager_instance = None
device_manager_instance = None

db_manager_lock = threading.Lock()
admin_manager_lock = threading.Lock()
device_manager_lock = threading.Lock()

def DBManager():
    global db_manager_instance
    with db_manager_lock:
        if db_manager_instance is None:
            from Database.dbManager import DBManager
            db_manager_instance = DBManager()
    return db_manager_instance

def AdminManager():
    global admin_manager_instance
    with admin_manager_lock:
        if admin_manager_instance is None:
            from MasterServer.adminManagerInstance import AdminManagerInstance
            admin_manager_instance = AdminManagerInstance()
    return admin_manager_instance

def DeviceManager():
    global device_manager_instance
    with device_manager_lock:
        if device_manager_instance is None:
            from MasterServer.deviceManagerInstace import DeviceManagerInstance
            device_manager_instance = DeviceManagerInstance()
    return device_manager_instance
