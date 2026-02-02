from pydantic import BaseModel
from typing import Optional, List

class UpdateDeviceData(BaseModel):
    user_id: Optional[str] = ''
    device_id: str
    device_name: str
    device_token: Optional[str] = ''
    app_name: Optional[str] = ''
    account_numbers: Optional[List[str]] = []

class AccountRegisterationData(BaseModel):
    device_id: Optional[str] = ''
    device_name: Optional[str] = ''
    app_name: Optional[str] = ''
    account_number: Optional[str] = ''

class UpdateDeviceTokenData(BaseModel):
    user_id: Optional[str] = ''
    device_id: str
    device_token: Optional[str] = ''

class NotificationData(BaseModel):
    app_name: str 
    package_name: str
    title: str
    content: str
    device_id: str
    device_name: str = ""
    timestamp: str