import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import LabeledPrice
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

BOT_TOKEN = "1780247078:A3ywXHsuNsSJzuBNA-biafxh7ay72GqzdVd"
ADMIN_ID = 1780246929 # Замени на ТВОЙ_ID_ТУТ (без кавычек)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class DonateState(StatesGroup):
    waiting_for_amount = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    text = (
        "Что умеет этот бот?\n\n"
        "Пожертвуйте свои звёзды в фонд бедным пользователям StaticGram."
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="⭐ Пожертвовать", callback_data="donate")
    await message.answer(text, reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data == "donate")
async def process_donate(callback: types.CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="cancel")
    
    text = (
        "✍️ Укажите, сколько звёзд вы хотите пожертвовать в фонд бедным пользователям StaticGram.\n"
        "(от 10 до 100,000 ⭐️)\n\n"
        "*Введите число в чат:*"
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await state.set_state(DonateState.waiting_for_amount)

@dp.message(DonateState.waiting_for_amount)
async def process_amount(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Ошибка: введите число.")
        return

    amount = int(message.text)
    if amount < 10 or amount > 100000:
        await message.answer("Ошибка: сумма должна быть от 10 до 100,000.")
        return

    await state.clear()
    
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="cancel")
    builder.button(text="✅ Продолжить", callback_data=f"confirm_{amount}")
    
    text = (
        f"⚠️ Вы точно хотите пожертвовать {amount} ⭐️ в фонд бедным пользователям StaticGram?"
    )
    await message.answer(text, reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data.startswith("confirm_"))
async def process_confirm(callback: types.CallbackQuery):
    amount = int(callback.data.split("_")[1])
    
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Пожертвование звёзд",
        description=f"Пожертвование {amount} звёзд в фонд StaticGram",
        payload=f"donate_{amount}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Звёзды", amount=amount)],
        start_parameter="donate"
    )
    await callback.message.delete()

@dp.callback_query(lambda c: c.data == "cancel")
async def process_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Пожертвование отменено.")

@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(lambda message: message.successful_payment)
async def process_successful_payment(message: types.Message):
    payment_info = message.successful_payment
    amount = payment_info.total_amount
    
    text = (
        f"Спасибо, что пожертвовали {amount} ⭐️ в наш фонд бедным пользователям StaticGram!\n\n"
        f"Ваши звёзды успешно зачислены."
    )
    await message.answer(text)
    
    try:
        await bot.send_message(
            ADMIN_ID, 
            f"💰 Новый донат: {amount} звёзд от @{message.from_user.username}"
        )
    except:
        pass

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())