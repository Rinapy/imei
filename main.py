from multiprocessing import Process

import uvicorn

from infrastructure.telegram.bot import main as run_bot
from infrastructure.http import (
        api_server,
        external_api_repo,
        httpx_client
    )
from infrastructure.database import sqlite

from usecase.user import (
        GetUserToken,
        AddUserInWL,
        DellUserInWL,
        GetAvbServices,
        CheckIMEI,
        AddUser,
        GetUser
    )

def run_fastapi(check_imei, get_avb_services):
    # Создаем FastAPI приложение внутри процесса
    app = api_server.APIApp(check_imei, get_avb_services)
    uvicorn.run(app, host="0.0.0.0", port=8000)

def start_app():
    # Инициализация репозиториев
    db_repo = sqlite.SQLiteDataBaseRepository('sqlite.db')
    api_repo = external_api_repo.IMEICheckNet(httpx_client.HttpxClient())
    
    # Инициализация use cases
    get_user_token = GetUserToken(db_repo)
    add_user_in_wl = AddUserInWL(db_repo)
    del_user_in_wl = DellUserInWL(db_repo)
    add_user = AddUser(db_repo)
    get_user = GetUser(db_repo)
    check_imei = CheckIMEI(api_repo)
    get_avb_services = GetAvbServices(api_repo)
    
    # Запускаем FastAPI в отдельном процессе, передавая use cases
    fastapi_process = Process(
        target=run_fastapi, 
        args=(check_imei, get_avb_services)
    )
    fastapi_process.start()
    
    # Запускаем телеграм бота
    run_bot(
        use_case_get_user_token=get_user_token,
        use_case_add_user_in_wl=add_user_in_wl,
        use_case_del_user_in_wl=del_user_in_wl,
        use_case_check_imei=check_imei,
        use_case_add_user=add_user,
        use_case_get_user=get_user,
        use_case_get_avb_services=get_avb_services
    )

if __name__ == "__main__":
    start_app()
