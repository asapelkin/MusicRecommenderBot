import telebot
from telebot import types
import config
import lastfm
# import os.path

bot = telebot.TeleBot(config.token)
user_out_dict = dict() # словарь, ставящий в соответствие каждому пользователю полученный массив исполнителей/треков для дальнейшей работы
user_inp_dict = dict() # словарь, ставящий в соответствие каждому пользователю исходный массив исполнителей/треков для дальнейшей работы
waitAddFlag = dict() # флаги ожидания добавления нового искомого
stepNumItems = 10 # количество
error_text = "Композицию необходимо вводить в формате исполнитель - трек или просто имя исполнителя. Для поиска треков необходимо название композиции. Введите /help для получения подробной справки."

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    helpText = """
        Бот принимает на вход название одной или нескольких композиций и осуществляет\
         поиск похожих исполнителей или композиций используя ресурс LastFm.
        Для осуществления поиска необходимо ввести название композиции в формате\
        исполнитель - трек или просто имя исполнителя, после чего, при необходимости,\
        добавить еще одного исполнителя/композицию или начать поиск композиций или\
        исполнителя нажатием на соответствующию кнопку. Поиск исполнителей возможен \
        и по другним исполнителям и по композициям, тогда как поиск композиций возможен только по другим композициям.
    """
    bot.send_message(message.chat.id, helpText)


@bot.message_handler(content_types=["text"])
def text_handler(message): # обработчик текстовых сообщений

    #if waitAddFlag[message.chat.id]: # пришло добавление в исходный массив


    textMessage = message.text
    chat_id = message.chat.id
    print("Получено сообщение = " + textMessage)
    keyboard = types.InlineKeyboardMarkup()

    if len(user_inp_dict) == 0:
        user_inp_dict[message.chat.id] = [textMessage]
    else:
        user_inp_dict[message.chat.id].append(textMessage)

    artists_button = types.InlineKeyboardButton(text="Найти похожих исполнителей", callback_data="show artist " + textMessage)
    tracks_button = types.InlineKeyboardButton(text="Найти похожие треки", callback_data="show track " + textMessage)
    add_button = types.InlineKeyboardButton(text="Добавить еще один трек или исполнителя", callback_data="add " + textMessage)
    keyboard.add(artists_button)
    keyboard.add(tracks_button)
    keyboard.add(add_button)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    # if call.message:
    textMessArray = call.data.split(' ')
    action= ""
    if len(textMessArray) >= 1:
        action = textMessArray[0]

    if action == "show":
        showAction(call)
    elif action == "add":
        addAction(call)
    elif action == "next":
        sendNext(call)


def addAction(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите еще одну композицию или исполнителя.")
    waitAddFlag[call.message.chat.id] = True


def showAction(call):
    print("user_inp_dict")
    print(user_inp_dict)
    textMessArray = call.data.split(' ')
    method = ""

    if len(textMessArray) >= 2:
        method = textMessArray[1]

    if call.message.chat.id in user_inp_dict:
        user_out_dict[call.message.chat.id] = lastfm.getSimilarFromArray(config.lastFmKey, user_inp_dict[call.message.chat.id], method) #lastfm.getSimilar(config.lastFmKey, artist_name, track_name, method)

    user_inp_dict.clear()
    #if len(user_out_dict[call.message.chat.id]):
    call.data = "next " + method
    sendNext(call)




def sendNext(call):
    textMessArray = call.data.split(' ')
    method = ""
    if len(textMessArray) >= 2:
        method = textMessArray[1]

    if not call.message.chat.id in user_out_dict:
        return

    num_items = min(len(user_out_dict[call.message.chat.id]), stepNumItems)

    print("num_items = " + str(num_items))

    if method == "artist":
        if not num_items:
            text = "Похожих исполнитей не найдено! " + error_text
        else:
            text = "Похожие исполнители:"
    else:
        if not num_items:
            text = "Похожих треков не найдено! " + error_text
        else:
            text = "Похожие треки:"

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text)

    if method == "artist":
        for i in range(0, num_items):
            print(user_out_dict[call.message.chat.id][i].name)
            print(user_out_dict[call.message.chat.id][i].image)
            print(user_out_dict[call.message.chat.id][i].url)
            print()
            mess2send = user_out_dict[call.message.chat.id][i].name + " \n" + user_out_dict[call.message.chat.id][i].url
            bot.send_message(call.message.chat.id, mess2send, disable_web_page_preview=True)
            ## bot.send_photo(call.message.chat.id, usersArrays[call.message.chat.id][i].image)
    elif method == "track":
        for i in range(0, num_items):
            print(user_out_dict[call.message.chat.id][i].artist)
            print(user_out_dict[call.message.chat.id][i].name)
            print(user_out_dict[call.message.chat.id][i].image)
            print(user_out_dict[call.message.chat.id][i].url)
            print()
            mess2send = user_out_dict[call.message.chat.id][i].artist + " - " + user_out_dict[call.message.chat.id][i].name + " \n" + \
                        user_out_dict[call.message.chat.id][i].url
            bot.send_message(call.message.chat.id, mess2send, disable_web_page_preview=True)
            ## bot.send_photo(call.message.chat.id, usersArrays[call.message.chat.id][i].image)
    else:
        return

    user_out_dict[call.message.chat.id] = user_out_dict[call.message.chat.id][num_items:]

    if len(user_out_dict[call.message.chat.id]) > 0:
        keyboard = types.InlineKeyboardMarkup()
        next_button = types.InlineKeyboardButton(text="Показать еще " + str(stepNumItems),
                                                 callback_data="next " + method)
        keyboard.add(next_button)
        bot.send_message(call.message.chat.id, "...", reply_markup=keyboard)


if __name__ == '__main__':
    bot.polling(none_stop=True)
    #
    # result = [1,2,3,4,5,6]
    #
    # for i in range(len(result)):
    #     for array in com_array[1:]:
    #         for comp in array:
    #             if not result[i] == comp:
    #                 result = result[:i-1] + result[i+1:]
    #                 i = i-1

