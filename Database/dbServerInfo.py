import json, logging, uuid
import Utils.generalUtils as GeneralUtils

from packaging import version
from loggingSystem import LoggingSystem
from Models.serverInfo import ServerInfo, ServerConfig, UserConfig
from pydantic_core import from_json

class DBServerInfo:
    def __init__(self):
        self.loadServerInfo()
        self.loadServerConfig()
        self.loadAdminKeys()
        self.loadPairKeys()
        self.app_version = version.parse(self.server_info.version)

    def loadServerInfo(self):
        try:
            with open(GeneralUtils.getPath("Assets/serverInfo.json")) as file:
                self.server_info = ServerInfo.model_validate(from_json(file.read()))
        except:
            self.server_info = None
            LoggingSystem.serverLog(logging.ERROR, 'Load server info json failed.')

    def loadServerConfig(self):
        try:
            with open(GeneralUtils.getPath("Assets/serverConfig.json")) as file:
                self.server_config = ServerConfig.model_validate(json.loads(file.read()))
        except:
            self.server_config = None
            LoggingSystem.serverLog(logging.ERROR, 'Load server config json failed.')

    def loadAdminKeys(self):
        try:
            self.admin_keys = []
            with open(GeneralUtils.getPath("Assets/adminKeys.json")) as file:
                admin_keys = json.loads(file.read()).get("admin_keys", [])
                for admin_key in admin_keys:
                    admin_key_decoded = uuid.uuid5(uuid.NAMESPACE_X500, admin_key).hex
                    self.admin_keys.append(admin_key_decoded)
        except:
            self.admin_keys = []
            LoggingSystem.serverLog(logging.ERROR, 'Load admin keys json failed.')

    def loadPairKeys(self):
        try:
            self.pair_keys = []
            with open(GeneralUtils.getPath("Assets/appPairKeys.json")) as file:
                pair_keys = json.loads(file.read()).get("pair_keys", [])
                for pair_key in pair_keys:
                    pair_key_decoded = uuid.uuid5(uuid.NAMESPACE_X500, pair_key).hex
                    self.pair_keys.append(pair_key_decoded)
        except:
            self.pair_keys = []
            LoggingSystem.serverLog(logging.ERROR, 'Load app pair keys json failed.')
            
    def verifyAdminKey(self, admin_key):
        admin_key = uuid.uuid5(uuid.NAMESPACE_X500, admin_key).hex
        if admin_key in self.admin_keys:
            return True
            
        return False
    
    def verifyAppPairKey(self, app_pair_key):
        app_pair_key = uuid.uuid5(uuid.NAMESPACE_X500, app_pair_key).hex
        if app_pair_key in self.pair_keys:
            return True
            
        return False
    
    def versionAtLeast(self, compare_version: str) -> bool:
        if self.server_info and self.app_version <= version.parse(compare_version):
            return True
            
        return False
    
    def getUserDomain(self, is_production: bool) -> str | None:
        if self.server_config:
            if is_production:
                return self.server_config.domain_production
            else:
                return self.server_config.domain_uat
            
        return None