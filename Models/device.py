from pydantic import BaseModel
from typing import List, Optional

class App(BaseModel):
    bank_code: str
    app_name: str
    external_app_name: Optional[str] = ''
    account_list: List[str]

    def to_dict(self):
        return {
            "bank_code": self.bank_code,
            "app_name": self.app_name,
            "external_app_name": self.external_app_name,
            "account_list": self.account_list
        }

class Devices(BaseModel):
    token: str = ""
    name: str = ""
    apps: List[App]