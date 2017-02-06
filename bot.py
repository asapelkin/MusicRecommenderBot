import telebot
import config
# import os.path

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    bot.send_message(message.chat.id, "@todo")


@bot.message_handler(content_types=["text"])
def text_handler(message): # обработчик текстовых сообщений
    textMessage = message.text
    chat_id = message.chat.id

    print("Получено сообщение = " + textMessage) # only for debug

    bot.send_message(message.chat.id, textMessage)

    
if __name__ == '__main__':
     bot.polling(none_stop=True)



# try:
        # output = octave_session.eval(command, return_both=True, timeout=10)[0]
    # except BaseException:
        #output = "Syntax error"