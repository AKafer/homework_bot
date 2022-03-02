from ssl import VerifyMode
from telegram import Bot

# Здесь укажите токен, 
# который вы получили от @Botfather при создании бот-аккаунта
bot = Bot(token='5298286443:AAGoasP7nhX6ciQ6GO47KdDotLJjQp5WyYE')
# Укажите id своего аккаунта в Telegram
chat_id = 749706860
text = 'Вам телеграмма!'
# Отправка сообщения
bot.send_message(chat_id)