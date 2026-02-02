from Database.dbServerInfo import DBServerInfo
from Database.dbBanks import DBBanksInfo
from Database.dbDevices import DBDevicesInfo

class DBManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls)
            cls._instance.init()
        return cls._instance
    
    def init(self):
        self.server_info_db = DBServerInfo()
        self.bank_info_db = DBBanksInfo()
        self.app_notification_info_db = DBDevicesInfo()