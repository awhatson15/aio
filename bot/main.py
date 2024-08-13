import asyncio
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aiogram import Bot, Dispatcher
from config.config import BOT_TOKEN, CHAT_ID, SETTINGS, EXCHANGES
from ccxt import kucoin, bitmart
from bot.utils import get_exchange_client
from bot.handlers import router  # Импортируем наш роутер из handlers

# Настройка логирования
logging.basicConfig(level=logging.INFO, filename='logs/bot.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')



# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Подключение роутера
dp.include_router(router)

async def check_prices():
    while True:
        try:
            exchange1_client = get_exchange_client(kucoin if SETTINGS["exchange1"] == "KuCoin" else bitmart, EXCHANGES[SETTINGS["exchange1"]])
            exchange2_client = get_exchange_client(kucoin if SETTINGS["exchange2"] == "KuCoin" else bitmart, EXCHANGES[SETTINGS["exchange2"]])

            price1 = exchange1_client.fetch_ticker(SETTINGS["base_currency"])['bid']
            price2 = exchange2_client.fetch_ticker(SETTINGS["base_currency"])['bid']

            if price2 < price1 * (1 - SETTINGS["price_diff_threshold"]):
                buy_price = price1 * (1 - SETTINGS["buy_discount"])
                logging.info(f"Условие выполнено: цена на {SETTINGS['exchange2']} {price2} ниже на {SETTINGS['price_diff_threshold']*100}% чем на {SETTINGS['exchange1']} {price1}. Покупаем по {buy_price}")
                
                order = exchange2_client.create_limit_buy_order(SETTINGS["base_currency"], amount=0.001, price=buy_price)
                
                await bot.send_message(chat_id=CHAT_ID, text=f"Ордер на покупку: {order}")
                
                await asyncio.sleep(30)
                current_price = exchange2_client.fetch_ticker(SETTINGS["base_currency"])['bid']
                if current_price >= buy_price * (1 + SETTINGS["sell_threshold"]):
                    sell_order = exchange2_client.create_limit_sell_order(SETTINGS["base_currency"], amount=0.001, price=current_price)
                    await bot.send_message(chat_id=CHAT_ID, text=f"Ордер на продажу: {sell_order}")
                else:
                    await bot.send_message(chat_id=CHAT_ID, text=f"Цена не выросла, возможно нужно переводить на {SETTINGS['exchange1']} для продажи")
            else:
                logging.info("Условия для покупки не выполнены.")
        
        except Exception as e:
            logging.error(f"Ошибка при проверке цен: {e}")
        
        await asyncio.sleep(SETTINGS["check_interval"])

async def on_startup():
    asyncio.create_task(check_prices())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(on_startup())
