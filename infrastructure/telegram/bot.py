from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from infrastructure.settings import TELEGRAM_BOT_TOKEN, ADMIN_TG_ID
from usecase.user import GetUserToken, AddUserInWL, DellUserInWL, CheckIMEI, AddUser, GetUser, GetAvbServices
from entities.models import ApiCheckIMEIRequestModel, ApiInvalidResponseModel
from datetime import datetime


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, use_case_add_user: AddUser):
    user_id = update.effective_user.id
    res = use_case_add_user.execute(user_id)
    print(res)
    if res:
        await update.message.reply_text("Добро пожаловать! Отправьте IMEI для проверки")
    else:
        await update.message.reply_text("В данный момент бот не доступен.")


async def handle_imei(update: Update, context: ContextTypes.DEFAULT_TYPE, use_case_check_imei: CheckIMEI, use_case_get_user: GetUser, use_case_get_avb_services: GetAvbServices):
    try:
        user_id = update.effective_user.id
        perm_level = use_case_get_user.execute(user_id)

        if perm_level != 1 and str(user_id) != ADMIN_TG_ID:
            await update.message.reply_text(f"У вас недостаточно прав для проверки IMEI")
            return

        # Сохраняем IMEI для последующей проверки
        context.user_data['requst_data'] = ApiCheckIMEIRequestModel(
            deviceId=update.message.text)
    except ValueError as e:
        await update.message.reply_text(f'{e}')
        return

    try:
        # Получаем доступные сервисы
        services = await use_case_get_avb_services.execute()

        # Создаем клавиатуру
        keyboard = []
        for service in services:
            keyboard.append([InlineKeyboardButton(
                f"{service.title} ({service.price}$)",
                callback_data=f"service_{service.id}"
            )])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Выберите сервис для проверки:",
            reply_markup=reply_markup
        )

    except Exception as e:
        await update.message.reply_text("Произошла ошибка при обработке запроса.\nПостараемся испраить как можно скорее")

        # Отправляем детали ошибки администратору
        if ADMIN_TG_ID:
            admin_error_message = (
                f"Ошибка у пользователя {update.effective_user.id}:\n"
                f"Команда: {update.message.text}\n"
                f"Ошибка: {str(e)}"
            )
            try:
                await context.bot.send_message(
                    chat_id=ADMIN_TG_ID,
                    text=admin_error_message
                )
            except Exception as admin_error:
                print(f"Не удалось отправить сообщение администаратору: {
                      str(admin_error)}")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, use_case_check_imei: CheckIMEI):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("service_"):
        service_id = int(query.data.split("_")[1])
        requst_data = context.user_data.get('requst_data')

        if not requst_data:
            await query.message.reply_text("Пожалуйста, отправьте IMEI заново")
            return

        try:
            requst_data.serviceId = service_id
            result = await use_case_check_imei.execute(requst_data)

            if isinstance(result, ApiInvalidResponseModel):
                error_msg = "\n".join(
                    [f"{k}: {', '.join(v)}" for k, v in result.errors.items()])
                await query.message.reply_text(f"Ошибка проверки:\n{error_msg}")
            else:
                # Конвертация Unix timestamp в читаемый формат
                purchase_date = datetime.fromtimestamp(
                    result.properties.estPurchaseDate
                ).strftime('%d.%m.%Y') if result.properties.estPurchaseDate else 'Неизвестно'

                processed_date = datetime.fromtimestamp(
                    result.processedAt
                ).strftime('%d.%m.%Y %H:%M:%S')

                response_text = (
                    f"ID: {result.id}\n"
                    f"Тип: {result.type}\n"
                    f"Статус: {result.status}\n"
                    f"ID заказа: {result.orderId}\n"
                    f"Сервис: {result.service.title}\n"
                    f"Цена: {result.amount}$\n"
                    f"IMEI/SN: {result.deviceId}\n"
                    f"Время обработки: {processed_date}\n\n"
                    f"Информация об устройстве:\n"
                    f"Модель: {result.properties.deviceName}\n"
                    f"Изображение: {result.properties.image}\n"
                    f"IMEI: {result.properties.imei}\n"
                    f"Дата покупки: {purchase_date}\n"
                    f"SIM Lock: {
                        'Да' if result.properties.simLock else 'Нет'}\n"
                    f"Гарантия: {result.properties.warrantyStatus}\n"
                    f"Ремонтное покрытие: {
                        'Да' if result.properties.repairCoverage else 'Нет'}\n"
                    f"Тех. поддержка: {
                        'Да' if result.properties.technicalSupport else 'Нет'}\n"
                    f"Описание модели: {result.properties.modelDesc}\n"
                    f"Демо устройство: {
                        'Да' if result.properties.demoUnit else 'Нет'}\n"
                    f"Восстановленное: {
                        'Да' if result.properties.refurbished else 'Нет'}\n"
                    f"Страна покупки: {
                        result.properties.purchaseCountry or 'Неизвестно'}\n"
                    f"Регион: {
                        result.properties.apple_region or 'Неизвестно'}\n"
                    f"Find My iPhone: {
                        'Включен' if result.properties.fmiOn else 'Выключен'}\n"
                    f"Режим пропажи: {
                        'Включен' if result.properties.lostMode else 'Выключен'}\n"
                    f"Статус блокировки USA: {
                        result.properties.usaBlockStatus or 'Неизвестно'}\n"
                    f"Сеть: {result.properties.network}"
                )
                await query.message.reply_text(response_text)

            del context.user_data['requst_data']
        except Exception as e:
            print(e)
            await query.message.reply_text("Произошла ошибка при обработке запроса.\nПостараемся исправить как можно скорее")

            # Отправляем детали ошибки администратору
            if ADMIN_TG_ID:
                admin_error_message = (
                    f"Ошибка у пользователя {update.effective_user.id}:\n"
                    f"Callback data: {query.data}\n"
                    f"Ошибка: {str(e)}"
                )
                try:
                    await context.bot.send_message(
                        chat_id=ADMIN_TG_ID,
                        text=admin_error_message
                    )
                except Exception as admin_error:
                    print(f"Не удалось отправить сообщение администратору: {
                          str(admin_error)}")


async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE, use_case_add_user_in_wl: AddUserInWL):
    if str(update.effective_user.id) != ADMIN_TG_ID:
        await update.message.reply_text("У вас нет прав для этой команды")
        return

    try:
        user_id = int(context.args[0])
        result = use_case_add_user_in_wl.execute(user_id)
        if result:
            await update.message.reply_text(f"Пользователь {user_id} добавлен в белый список")
        else:
            await update.message.reply_text(f"Не удалось добавить пользователя {user_id} в белый список")
    except (ValueError, IndexError):
        await update.message.reply_text("Использование: /add_user <user_id>")


async def del_user(update: Update, context: ContextTypes.DEFAULT_TYPE, use_case_del_user: DellUserInWL):
    if str(update.effective_user.id) != ADMIN_TG_ID:
        await update.message.reply_text("У вас нет прав для этой команды")
        return

    try:
        user_id = int(context.args[0])
        use_case_del_user.execute(user_id)
        await update.message.reply_text(f"Пользователь {user_id} удален из белого списка")
    except (ValueError, IndexError):
        await update.message.reply_text("Использование: /del_user <user_id>")


async def get_user_token(update: Update, context: ContextTypes.DEFAULT_TYPE, use_case_get_user_token: GetUserToken):
    user_id = update.effective_user.id
    token = use_case_get_user_token.execute(user_id)
    if not token:
        await update.message.reply_text(f"Перезапустите бота через /start")
        return
    await update.message.reply_text(f"Ваш API Токен: {token}")


def main(
        use_case_get_user_token: GetUserToken,
        use_case_add_user_in_wl: AddUserInWL,
        use_case_del_user_in_wl: DellUserInWL,
        use_case_check_imei: CheckIMEI,
        use_case_add_user: AddUser,
        use_case_get_user: GetUser,
        use_case_get_avb_services: GetAvbServices,):

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start",
                                           lambda update, context: start(update, context, use_case_add_user)))
    application.add_handler(CommandHandler("add_user",
                                           lambda update, context: add_user(update, context, use_case_add_user_in_wl)))
    application.add_handler(CommandHandler("del_user",
                                           lambda update, context: del_user(update, context, use_case_del_user_in_wl)))
    application.add_handler(CommandHandler("token",
                                           lambda update, context: get_user_token(update, context, use_case_get_user_token)))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,
                                           lambda update, context: handle_imei(update, context, use_case_check_imei, use_case_get_user, use_case_get_avb_services)))
    application.add_handler(CallbackQueryHandler(
        lambda update, context: button_callback(
            update, context, use_case_check_imei)
    ))

    application.run_polling()


if __name__ == '__main__':
    main()
