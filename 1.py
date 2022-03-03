# from telegram import Bot
import datetime as DT

dt = DT.datetime.fromisoformat('2022-02-16 15:51:27')
dt = dt.replace(tzinfo=DT.timezone.utc)
print(dt)
print(dt.timestamp())
print(int(dt.timestamp()))

"""
# Здесь укажите токен,
# # который вы получили от @Botfather при создании бот-аккаунта
bot = Bot(token='5298286443:AAGoasP7nhX6ciQ6GO47KdDotLJjQp5WyYE')
# Укажите id своего аккаунта в Telegram
chat_id = 749706860
text = 'Вам телеграмма!'
# Отправка сообщения
bot.send_message(chat_id)."""
