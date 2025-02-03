from typing import Protocol, Dict, Any, Optional
from abc import abstractmethod

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