import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# =========================================================
# КОНФИГУРАЦИЯ И НАСТРОЙКИ
# =========================================================
TOKEN = "8486773145:AAG1DTcyB1HcLU2briUAKCoaDfAi_Kz4SqY"
MY_CHAT_ID = 414880465 # Твой ID для уведомлений

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Временная база данных в оперативной памяти
db = {
    "total_profit": 0, 
    "total_orders": 0
}

# =========================================================
# СОСТОЯНИЯ (FSM) - ПОШАГОВАЯ ФОРМА ЗАКАЗА
# =========================================================
class OrderState(StatesGroup):
    service = State()  # Тип услуги
    rooms = State()    # Кол-во комнат
    windows = State()  # Кол-во окон
    area = State()     # Площадь объекта
    confirm = State()  # Подтверждение цены
    address = State()  # Адрес и время
    phone = State()    # Номер телефона

# =========================================================
# КЛАВИАТУРЫ (REPLY)
# =========================================================
def main_kb(user_id):
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🧮 Рассчитать стоимость / Заказать"))
    builder.row(
        types.KeyboardButton(text="📸 До/После"), 
        types.KeyboardButton(text="⭐ Отзывы")
    )
    builder.row(
        types.KeyboardButton(text="✨ О нас"), 
        types.KeyboardButton(text="👤 Личный кабинет")
    )
    
    # Кнопка админки видна только тебе
    if user_id == MY_CHAT_ID:
        builder.row(types.KeyboardButton(text="👨‍💻 Админка"))
        
    return builder.as_markup(resize_keyboard=True)

# =========================================================
# ОСНОВНЫЕ ОБРАБОТЧИКИ КОМАНД
# =========================================================
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Приветствуем в CleanHub Хабаровск! ✨\n"
        "Мы сделаем ваш дом идеально чистым. Выберите нужное действие в меню ниже:", 
        reply_markup=main_kb(message.from_user.id)
    )

@dp.message(F.text == "❌ Отмена")
async def global_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Действие отменено. Вы возвращены в главное меню.", 
        reply_markup=main_kb(message.from_user.id)
    )

# =========================================================
# ИНФОРМАЦИОННЫЕ КНОПКИ МЕНЮ
# =========================================================
@dp.message(F.text == "✨ О нас")
async def about_btn(message: types.Message):
    await message.answer(
        "🧹 **CleanHub** — это команда профессионалов из Хабаровска.\n\n"
        "Мы используем только качественную химию и современное оборудование. "
        "Наш приоритет — ваш уют и чистота вашего дома!"
    )

@dp.message(F.text == "⭐ Отзывы")
async def reviews_btn(message: types.Message):
    await message.answer(
        "⭐ У нас сотни довольных клиентов!\n\n"
        "Посмотреть реальные отзывы или оставить свой вы сможете "
        "сразу после того, как мы выполним ваш заказ."
    )

@dp.message(F.text == "📸 До/После")
async def cases_btn(message: types.Message):
    await message.answer(
        "📸 Наши работы говорят сами за себя!\n\n"
        "Посмотреть портфолио в Instagram: [ССЫЛКА]"
    )

@dp.message(F.text == "👤 Личный кабинет")
async def profile_btn(message: types.Message):
    status = "Администратор" if message.from_user.id == MY_CHAT_ID else "Клиент"
    await message.answer(
        f"👤 **Ваш профиль**\n\n"
        f"🆔 Ваш ID: `{message.from_user.id}`\n"
        f"🎭 Ваш статус: {status}\n"
        f"📊 Заказов в системе: {db['total_orders']}", 
        parse_mode="Markdown"
    )

@dp.message(F.text == "👨‍💻 Админка")
async def admin_btn(message: types.Message):
    if message.from_user.id != MY_CHAT_ID:
        return
    await message.answer(
        f"📊 **ПАНЕЛЬ УПРАВЛЕНИЯ**\n\n"
        f"✅ Выполнено заказов: {db['total_orders']}\n"
        f"💰 Общая прибыль: {db['total_profit']}₽"
    )

# =========================================================
# ЛОГИКА ОФОРМЛЕНИЯ ЗАКАЗА
# =========================================================
@dp.message(F.text == "🧮 Рассчитать стоимость / Заказать")
async def order_start_step(message: types.Message, state: FSMContext):
    b = ReplyKeyboardBuilder()
    b.row(types.KeyboardButton(text="🏢 Уборка офисов"), types.KeyboardButton(text="🏠 Поддерживающая"))
    b.row(types.KeyboardButton(text="✨ Генеральная"), types.KeyboardButton(text="🧱 После ремонта"))
    b.row(types.KeyboardButton(text="❌ Отмена"))
    
    await message.answer(
        "Выберите тип необходимой уборки:", 
        reply_markup=b.as_markup(resize_keyboard=True)
    )
    await state.set_state(OrderState.service)

@dp.message(OrderState.service)
async def order_rooms_step(message: types.Message, state: FSMContext):
    await state.update_data(service=message.text)
    await message.answer(
        "Укажите количество комнат или помещений:", 
        reply_markup=ReplyKeyboardBuilder().row(types.KeyboardButton(text="❌ Отмена")).as_markup(resize_keyboard=True)
    )
    await state.set_state(OrderState.rooms)

@dp.message(OrderState.rooms)
async def order_windows_step(message: types.Message, state: FSMContext):
    await state.update_data(rooms=message.text)
    await message.answer("Сколько окон необходимо помыть?")
    await state.set_state(OrderState.windows)

@dp.message(OrderState.windows)
async def order_area_step(message: types.Message, state: FSMContext):
    await state.update_data(windows=message.text)
    await message.answer("Укажите примерную площадь объекта (м²):")
    await state.set_state(OrderState.area)

@dp.message(OrderState.area)
async def order_confirm_step(message: types.Message, state: FSMContext):
    val = message.text.strip()
    if not val.isdigit():
        await message.answer("⚠️ Ошибка! Введите площадь только цифрами (например: 50):")
        return
    
    data = await state.get_data()
    area = int(val)
    
    # Логика цен
    prices = {"🏢 Уборка офисов": 120, "🧱 После ремонта": 150, "✨ Генеральная": 100, "🏠 Поддерживающая": 100}
    rate = prices.get(data['service'], 100)
    
    total_price = (area * rate) + (int(data.get('windows', 0)) * 500)
    await state.update_data(total=total_price)
    
    confirm_kb = ReplyKeyboardBuilder().row(
        types.KeyboardButton(text="✅ Оформить"), 
        types.KeyboardButton(text="❌ Отмена")
    )
    
    await message.answer(
        f"💰 **Предварительный расчет:**\n\n"
        f"Тип: {data['service']}\n"
        f"Площадь: {area} м²\n"
        f"Итоговая стоимость: {total_price}₽\n\n"
        f"Желаете оформить заказ?", 
        reply_markup=confirm_kb.as_markup(resize_keyboard=True),
        parse_mode="Markdown"
    )
    await state.set_state(OrderState.confirm)

@dp.message(OrderState.confirm, F.text == "✅ Оформить")
async def order_address_step(message: types.Message, state: FSMContext):
    await message.answer(
        "Укажите точный адрес и желаемое время уборки:", 
        reply_markup=ReplyKeyboardBuilder().row(types.KeyboardButton(text="❌ Отмена")).as_markup(resize_keyboard=True)
    )
    await state.set_state(OrderState.address)

@dp.message(OrderState.address)
async def order_phone_step(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Введите ваш номер телефона для связи:")
    await state.set_state(OrderState.phone)

@dp.message(OrderState.phone)
async def order_final_step(message: types.Message, state: FSMContext):
    data = await state.get_data()
    total = data['total']
    profit = int(total * 0.20)
    
    # Обновляем статистику
    db["total_orders"] += 1
    db["total_profit"] += profit

    # Кнопки управления для тебя
    admin_action_kb = InlineKeyboardBuilder()
    admin_action_kb.row(
        types.InlineKeyboardButton(text="✅ Выполнено", callback_data=f"order_done_{message.from_user.id}"),
        types.InlineKeyboardButton(text="❌ Отклонить", callback_data=f"order_fail_{message.from_user.id}")
    )

    # Отправка уведомления админу
    await bot.send_message(
        MY_CHAT_ID, 
        f"🆕 **ПОСТУПИЛ НОВЫЙ ЗАКАЗ!**\n\n"
        f"🛠 Услуга: {data['service']}\n"
        f"💰 Сумма: {total}₽\n"
        f"💳 Твоя доля (20%): {profit}₽\n"
        f"📍 Адрес: {data['address']}\n"
        f"📞 Тел: {message.text}", 
        reply_markup=admin_action_kb.as_markup(),
        parse_mode="Markdown"
    )
    
    await message.answer(
        "✅ Заявка успешно отправлена!\n"
        "Наш менеджер свяжется с вами в ближайшее время.", 
        reply_markup=main_kb(message.from_user.id)
    )
    await state.clear()

# =========================================================
# ОБРАБОТКА ДЕЙСТВИЙ АДМИНИСТРАТОРА (CALLBACKS)
# =========================================================
@dp.callback_query(F.data.startswith("order_done_"))
async def handle_order_done(callback: types.CallbackQuery):
    client_id = callback.data.split("_")[2]
    
    # Обновляем сообщение у админа
    await callback.message.edit_text(
        callback.message.text + "\n\n🏁 **СТАТУС: ВЫПОЛНЕНО**"
    )
    
    # Сообщение клиенту со ссылкой на отзыв
    await bot.send_message(
        client_id, 
        "🌟 **Ваш заказ выполнен!**\n\n"
        "Мы старались сделать ваш дом чище. Будем очень признательны, "
        "если вы оставите отзыв о нашей работе: [ТВОЯ_ССЫЛКА_НА_ОТЗЫВЫ]"
    )
    await callback.answer("Заказ завершен успешно!")

@dp.callback_query(F.data.startswith("order_fail_"))
async def handle_order_fail(callback: types.CallbackQuery):
    await callback.message.edit_text(
        callback.message.text + "\n\n❌ **СТАТУС: ОТКЛОНЕН**"
    )
    await callback.answer("Заказ отклонен.")

# =========================================================
# ЗАПУСК БОТА
# =========================================================
async def main():
    logging.basicConfig(level=logging.INFO)
    print("-----------------------------------------")
    print("🚀 CleanHub Хабаровск запущен и готов!")
    print(f"👨‍💻 ID Администратора: {MY_CHAT_ID}")
    print("-----------------------------------------")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен вручную.")