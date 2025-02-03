from fastapi import FastAPI, HTTPException

from usecase.user import CheckIMEI, GetAvbServices
from entities.models import ApiCheckIMEIModel, ApiCheckIMEIRequestModel
from utils.token_gen import decode_jwt


class APIApp(FastAPI):

    def __init__(self,
                 use_case_check_imei: CheckIMEI,
                 use_case_get_avb_services: GetAvbServices,
                 ):
        self.use_case_check_imei = use_case_check_imei
        self.use_case_get_avb_services = use_case_get_avb_services
        super().__init__()
        self._init_routes()

    def _init_routes(self):
        self.post("/api/check-imei")(self.check_imei)
        self.get("/api/services")(self.get_services)

    async def check_imei(self, check_imei_data: ApiCheckIMEIModel):
        if not check_imei_data.deviceId and not check_imei_data.token:
            raise HTTPException(status_code=400, detail={
                                'errorMessage': 'token and IMEI are required'})

        token_payload = decode_jwt(check_imei_data.token)
        if isinstance(token_payload, str):
            raise HTTPException(status_code=401, detail={
                                'errorMessage': token_payload})

        external_payload = ApiCheckIMEIRequestModel(
            deviceId=check_imei_data.deviceId,
            serviceId=check_imei_data.serviceId
        )
        return await self.use_case_check_imei.execute(external_payload)

    async def get_services(self):
        try:
            services = await self.use_case_get_avb_services.execute()
            return {"services": services}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
