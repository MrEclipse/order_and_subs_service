# bot.py

import os
import json
import asyncio
import logging

import aio_pika
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

# ———————————————
# Логирование
# ———————————————
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ———————————————
# Настройка SQLAlchemy
# ———————————————
POSTGRES = {
    "user": os.getenv("POSTGRES_USER"),
    "pass": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "db":   os.getenv("POSTGRES_DB"),
}

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{POSTGRES['user']}:{POSTGRES['pass']}@"
    f"{POSTGRES['host']}:{POSTGRES['port']}/"
    f"{POSTGRES['db']}"
)

engine = create_engine(DATABASE_URL, echo=True, future=True)
metadata = MetaData()
# отражаем только таблицу users_customuser
metadata.reflect(bind=engine, only=["users_customuser"])
Base = automap_base(metadata=metadata)
Base.prepare()
CustomUser = Base.classes.users_customuser

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)

# ———————————————
# Настройка бота aiogram
# ———————————————
tg_token = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=tg_token)
dp = Dispatcher()

contact_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📱 Поделиться номером", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    chat_id = message.from_user.id

    def check_registered():
        db = SessionLocal()
        try:
            return db.query(CustomUser).filter_by(telegram_id=str(chat_id)).first() is not None
        finally:
            db.close()

    if await asyncio.to_thread(check_registered):
        await message.answer("Вы уже зарегистрированы в системе.", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(
            "Для регистрации нажмите кнопку и поделитесь своим номером телефона:",
            reply_markup=contact_kb
        )

@dp.message(lambda m: m.contact is not None)
async def contact_handler(message: types.Message):
    phone = message.contact.phone_number
    chat_id = message.from_user.id

    def db_work():
        db = SessionLocal()
        try:
            user = db.query(CustomUser).filter_by(phone=phone).first()
            if not user:
                return 404
            if user.telegram_id and user.telegram_id != str(chat_id):
                return 400
            user.telegram_id = str(chat_id)
            db.add(user)
            db.commit()
            return 201
        finally:
            db.close()

    result = await asyncio.to_thread(db_work)
    remove_kb = ReplyKeyboardRemove()

    if result == 404:
        await message.answer("Пользователь с таким номером не найден.", reply_markup=remove_kb)
    elif result == 400:
        await message.answer("Этот номер уже привязан к другому аккаунту.", reply_markup=remove_kb)
    else:  # 201 или любые ошибки считаем успешной или единичной
        await message.answer("Вы успешно зарегистрированы в системе!", reply_markup=remove_kb)

# ———————————————
# Асинхронный консьюмер RabbitMQ через aio-pika
# ———————————————
async def rabbit_async_consumer():
    # читаем переменные окружения
    RABBIT = {
        "host": os.getenv("RABBITMQ_HOST", "rabbit"),
        "port": int(os.getenv("RABBITMQ_PORT", 5672)),
        "user": os.getenv("RABBITMQ_USER", "guest"),
        "pass": os.getenv("RABBITMQ_PASSWORD", "guest"),
        "vhost": os.getenv("RABBITMQ_VHOST", "/"),
    }
    connection = await aio_pika.connect_robust(
        host=RABBIT["host"],
        port=RABBIT["port"],
        login=RABBIT["user"],
        password=RABBIT["pass"],
        virtualhost=RABBIT["vhost"],
    )
    channel = await connection.channel()
    queue = await channel.declare_queue("orders_notifications", durable=True)
    logger.info("🐇 Rabbit consumer started, waiting for messages…")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                body = message.body
                logger.info(f"🐰 Received message: {body!r}")
                try:
                    data = json.loads(body)
                    tg_id = int(data["telegram_id"])
                    order = data.get("order_id")
                    text = f"Вам пришёл новый заказ №{order}" if order else "Вам пришёл новый заказ!"
                    await bot.send_message(chat_id=tg_id, text=text)
                except Exception:
                    logger.exception("❌ Failed to process Rabbit message")

# запускаем консьюмер при старте бота
@dp.startup()
async def on_startup():
    asyncio.create_task(rabbit_async_consumer())

# ———————————————
# Точка входа
# ———————————————
if __name__ == "__main__":
    dp.run_polling(bot)
