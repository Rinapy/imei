from typing import List
from infrastructure.settings import (
    EXTERNAL_API_URL_CHECK,
    EXTERNAL_SERVICE_TOKEN,
    EXTERNAL_API_URL_AVB_SERVICES
)
from entities.models import (
    ApiInvalidResponseModel,
    ApiValideResponseModel,
    ApiCheckIMEIRequestModel,
    ServiceModel
)
from protocols.repository import APIRepository
from protocols.http_client import HTTPClient


class IMEICheckNet(APIRepository):

    headers = {
        'Authorization': 'Bearer ' + EXTERNAL_SERVICE_TOKEN,
        'Content-Type': 'application/json'
    }

    def __init__(self, http_client: HTTPClient) -> None:
        self.http_client = http_client

    async def check_imei(
        self, request_model: ApiCheckIMEIRequestModel
    ) -> ApiValideResponseModel | ApiInvalidResponseModel:
        try:
            response = await self.http_client.post(
                EXTERNAL_API_URL_CHECK,
                json=request_model.model_dump(),
                headers=self.headers
            )
            print(response)
            # Проверяем наличие поля errors или message для определения типа ответа
            if isinstance(response, dict) and (
                'errors' in response or 'message' in response
            ):
                return ApiInvalidResponseModel(**response)
            return ApiValideResponseModel(**response)
        except Exception as e:
            return ApiInvalidResponseModel(errors={"error": [str(e)]})

    async def get_avb_services(self) -> List[ServiceModel]:
        response = await self.http_client.get(
            EXTERNAL_API_URL_AVB_SERVICES,
            headers=self.headers
        )
        return [ServiceModel(**service) for service in response]
