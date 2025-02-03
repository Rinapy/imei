from abc import abstractmethod
from typing import Protocol, Optional, Dict, Any, List

from entities.models import ApiInvalidResponseModel, ApiValideResponseModel, ApiCheckIMEIRequestModel, ServiceModel

class DataBaseRepository(Protocol):

    @abstractmethod
    def get_user_token(self, user_id: int) -> bool | str: ...

    @abstractmethod
    def add_user_in_wl(self, user_id: int) -> bool: ...

    @abstractmethod
    def del_user_in_wl(self, user_id: int) -> bool: ...

    @abstractmethod
    def get_user(self, user_id: int) -> bool | int: ...

    @abstractmethod
    def add_user(self, user_id: int) -> bool: ...





class HTTPClient(Protocol):
    """Протокол для HTTP клиента"""
    
    @abstractmethod
    async def post(
        self, 
        url: str, 
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Выполняет POST запрос
        
        Args:
            url: URL для запроса
            data: Данные формы (опционально)
            json: JSON данные (опционально)
            headers: Заголовки запроса (опционально)
            
        Returns:
            Dict с ответом от сервера
            
        Raises:
            HTTPException: При ошибках HTTP
            ConnectionError: При проблемах с подключением
        """
        ...

    @abstractmethod
    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Выполняет GET запрос
        
        Args:
            url: URL для запроса
            params: Query параметры (опционально)
            headers: Заголовки запроса (опционально)
            
        Returns:
            Dict с ответом от сервера
            
        Raises:
            HTTPException: При ошибках HTTP
            ConnectionError: При проблемах с подключением
        """
        ... 

class APIRepository(Protocol):

    @abstractmethod
    def __init__(self, http_client: HTTPClient) -> None: ...

    @abstractmethod
    def check_imei(
        self,
        request_model: ApiCheckIMEIRequestModel,
    ) -> ApiValideResponseModel | ApiInvalidResponseModel: ...

    @abstractmethod
    def get_avb_services(
        self,
    ) -> List[ServiceModel]: ...