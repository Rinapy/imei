from typing import List

from entities.models import ApiInvalidResponseModel, ApiValideResponseModel, ApiCheckIMEIRequestModel, ServiceModel
from protocols.repository import APIRepository, DataBaseRepository


class GetUserToken:

    def __init__(self, repo: DataBaseRepository) -> None:
        self.repo = repo

    def execute(self, user_id: int) -> bool | str:
        return self.repo.get_user_token(user_id)


class AddUserInWL:

    def __init__(self, repo: DataBaseRepository) -> None:
        self.repo = repo

    def execute(self, user_id: int) -> bool:
        return self.repo.add_user_in_wl(user_id)


class DellUserInWL:

    def __init__(self, repo: DataBaseRepository) -> None:
        self.repo = repo

    def execute(self, user_id: int) -> bool:
        return self.repo.del_user_in_wl(user_id)

class AddUser:

    def __init__(self, repo: DataBaseRepository) -> None:
        self.repo = repo

    def execute(self, user_id: int) -> bool:
        return self.repo.add_user(user_id)

class GetUser:

    def __init__(self, repo: DataBaseRepository) -> None:
        self.repo = repo

    def execute(self, user_id: int) -> bool | int:
        return self.repo.get_user(user_id)




class CheckIMEI:

    def __init__(self, repo: APIRepository) -> None:
        self.repo = repo

    def execute(
        self,
        request_model: ApiCheckIMEIRequestModel
    ) -> ApiValideResponseModel | ApiInvalidResponseModel:
        return self.repo.check_imei(request_model)

class GetAvbServices:

    def __init__(self, repo: APIRepository) -> None:
        self.repo = repo

    def execute(self,) -> List[ServiceModel]:
        return self.repo.get_avb_services()
