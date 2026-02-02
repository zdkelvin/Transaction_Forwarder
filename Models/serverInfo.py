from pydantic import BaseModel, RootModel
from typing import Dict

class ServerInfo(BaseModel):
    version: str
    server_ip: str
    server_port: int

class ServerConfig(BaseModel):
    production_mode: bool
    user: str
    secret_key: str
    domain_production: str
    domain_uat: str

class UserDomain(BaseModel):
    domain_production: str
    ip_production: str
    domain_uat: str
    ip_uat: str

class UserConfig(RootModel):
    root: Dict[str, UserDomain]