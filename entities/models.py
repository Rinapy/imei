from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional, Dict, List
from utils.token_gen import decode_jwt
import re


class ApiCheckIMEIModel(BaseModel):
    deviceId: str
    token: str
    serviceId: int

    @field_validator('token')
    @classmethod
    def validate_token(cls, v):
        result = decode_jwt(v)
        print(result)
        if isinstance(result, str):
            raise ValueError(result)
        return v

    @field_validator('deviceId')
    @classmethod
    def validate_deviceId(cls, v):
        if not re.match(r'^\d{8,15}$', v):
            raise ValueError('IMEI или S/N должен содержать от 8 до 15 цифр')
        return v


class ApiCheckIMEIRequestModel(BaseModel):
    deviceId: str
    serviceId: Optional[int] = None

    @field_validator('deviceId')
    @classmethod
    def validate_deviceId(cls, v):
        if not re.match(r'^\d{8,15}$', v):
            raise ValueError('IMEI или S/N должен содержать от 8 до 15 цифр')
        return v


class ErrorsModel(BaseModel):
    deviceId: List[str] = []


class ServiceModel(BaseModel):
    id: int
    title: str
    price: Optional[float] = None

    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError('Price cannot be negative')
        return v


class PropertiesModel(BaseModel):
    deviceName: str
    image: HttpUrl
    imei: Optional[str] = None
    estPurchaseDate: Optional[int] = None
    simLock: Optional[bool] = None
    warrantyStatus: Optional[str] = None
    repairCoverage: Optional[bool] = None
    technicalSupport: Optional[bool] = None
    modelDesc: Optional[str] = None
    demoUnit: Optional[bool] = None
    refurbished: Optional[bool] = None
    purchaseCountry: Optional[str] = None
    apple_region: Optional[str] = None
    fmiOn: Optional[bool] = None
    lostMode: Optional[bool] = None
    usaBlockStatus: Optional[str] = None
    network: Optional[str] = None


class ApiValideResponseModel(BaseModel):
    id: str
    type: str
    status: str
    orderId: Optional[str] = None
    service: ServiceModel
    amount: float
    deviceId: str
    processedAt: int
    properties: PropertiesModel


class ApiInvalidResponseModel(BaseModel):
    errors: Dict[str, List[str]]


# data = {
#     "id": "Nkas42_N32",
#     "type": "api",
#     "status": "successful",
#     "orderId": None,
#     "service": {
#         "id": 1,
#         "title": "Apple Basic Info",
#         "price": "0.10"
#     },
#     "amount": "0.10",
#     "deviceId": "123456789012345",
#     "processedAt": 41241252112,
#     "properties": {
#         "deviceName": "iPhone 11 Pro",
#         "image": "https://sources.imeicheck.net/image.jpg",
#         "imei": "123456789012345",
#         "estPurchaseDate": 1422349078,
#         "simLock": True,
#         "warrantyStatus": "AppleCare Protection Plan",
#         "repairCoverage": "false",
#         "technicalSupport": "false",
#         "modelDesc": "IPHONE 12 BLACK 64GB-JPN",
#         "demoUnit": True,
#         "refurbished": True,
#         "purchaseCountry": "Thailand",
#         "apple/region": "AT&T USA",
#         "fmiOn": True,
#         "lostMode": "false",
#         "usaBlockStatus": "Clean",
#         "network": "Global"
#     }
# }
