from pydantic import BaseModel, RootModel
from typing import Dict

class BankInfo(BaseModel):
    app_name: str
    package_name: str
    external_app_name: str

class BanksByCountry(BaseModel):
    country: Dict[str, BankInfo]

class SupportedBanks(RootModel[Dict[str, Dict[str, BankInfo]]]):
    pass