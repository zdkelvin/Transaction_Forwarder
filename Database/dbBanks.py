import logging
import Utils.generalUtils as GeneralUtils

from Models.bank import SupportedBanks
from loggingSystem import LoggingSystem
from pydantic_core import from_json

class DBBanksInfo:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBBanksInfo, cls).__new__(cls)
            cls._instance.loadSupportedBanks()
        return cls._instance
    
    def loadSupportedBanks(self):
        try:
            with open(GeneralUtils.getPath("Assets/supportedBankList.json")) as file:
                self.supported_banks = SupportedBanks.model_validate(from_json(file.read()))
        except Exception as e:
            self.supported_banks = None
            LoggingSystem.serverLog(logging.ERROR, f'Load supported bank list json failed: {str(e)}')