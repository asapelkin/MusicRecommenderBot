import telebot
from telebot import types
import config
import lastfm
import sqlite3

bot = telebot.TeleBot(config.token)
user_out_dict = dict() # словарь, ставящий в соответствие каждому пользователю полученный массив исполнителей/треков для дальнейшей работы
user_inp_dict = dict() # словарь, ставящий в соответствие каждому пользователю исходный массив исполнителей/треков для дальнейшей работы
waitAddFlag = dict() # флаги ожидания добавления нового искомого
stepNumItems = 10 # количество
error_text = "\nВозможно, неверный формат ввода. \n Для поиска похожих композиций необходимо вводить исходную композицию в формате исполнитель-трек. Для поиска похожих исполнителей возможен ввод только имени исполнителя. Введите /help для получения подробной справки."

def getUserSetting(chat_id, setname):
    db = sqlite3.connect(database)
    cursor = db.cursor()
    query = 'SELECT setvalue FROM user_settings WHERE user_id = ( SELECT user_id FROM users WHERE chat_id = "' + str(chat_id) + '") and set_id = ( SELECT set_id FROM settings WHERE setname = "' + str(setname) + '")'
    print(query)
    cursor.execute(query)
    res = cursor.fetchall()
    db.close()
    if len(res):
        return res[0][0]


def setUserSetting(chat_id, setname, setvalue):
    db = sqlite3.connect(database)
    cursor = db.cursor()
    query = 'INSERT OR REPLACE INTO user_settings (user_id, set_id, setvalue) VALUES (( SELECT user_id FROM users WHERE chat_id = "' + str(chat_id) + '"),  ( SELECT set_id FROM settings WHERE setname = "' + str(setname) + '"),  "' + str(setvalue) + '");'
    print(query)
    cursor.execute(query)
    db.commit()
    db.close()


def userAdd(chat_id):
    db = sqlite3.connect(database)
    cursor = db.cursor()
    query = 'SELECT * FROM users WHERE chat_id = '+str(chat_id)+';'
    print(query)
    cursor.execute(query)
    res = cursor.fetchall()
    print(res)
    if (len(res) == 0):
        print("Создаем нового пользователя!")
        cursor.execute('INSERT INTO users (chat_id) VALUES ("'+str(chat_id)+'");')
        db.commit()
        setUserSetting(chat_id, "show_photo", "1")
        setUserSetting(chat_id, "show_url", "1")
    db.close()


@bot.message_handler(commands=['photo_off'])
def handle_photo_off(message):
    setUserSetting(message.chat.id, "show_photo", "0")

@bot.message_handler(commands=['photo_on'])
def handle_photo_on(message):
    setUserSetting(message.chat.id, "show_photo", "1")

@bot.message_handler(commands=['url_off'])
def handle_url_off(message):
    setUserSetting(message.chat.id, "show_url", "0")

@bot.message_handler(commands=['url_on'])
def handle_url_on(message):
    setUserSetting(message.chat.id, "show_url", "1")

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    userAdd(message.chat.id)
    helpText = """
        Бот принимает на вход название одной или нескольких композиций и осуществляет \
        поиск похожих исполнителей или композиций используя ресурс LastFm.
        Для осуществления поиска необходимо ввести название композиции в формате \
        исполнитель - трек или просто имя исполнителя, после чего, при необходимости, \
        добавить еще одного исполнителя/композицию или начать поиск композиций/исполнителей \
        нажатием на соответствующию кнопку. Поиск исполнителей возможен \
        как по другим исполнителям, так и по композициям, тогда как поиск похожих композиций возможен только по другим композициям.

        Настройки:
        Для отключения вывода изображений введите команду:
        /photo_off
        Для включения введите:
        /photo_on

        Для отключения вывода ссылок введите команду:
        /url_off
        Для включения введите:
        /url_on
    """
    bot.send_message(message.chat.id, helpText)


@bot.message_handler(content_types=["text"])
def text_handler(message): # обработчик текстовых сообщений

    #if waitAddFlag[message.chat.id]: # пришло добавление в исходный массив

    textMessage = message.text
    chat_id = message.chat.id
    print("Получено сообщение = " + textMessage)
    keyboard = types.InlineKeyboardMarkup()

    if len(user_inp_dict) == 0: #  проверяем новое ли это сообщение, или добавление в список на поиск.
        user_inp_dict[message.chat.id] = [textMessage]
        userAdd(chat_id)
    else:
        user_inp_dict[message.chat.id].append(textMessage)

    artists_button = types.InlineKeyboardButton(text="Найти похожих исполнителей", callback_data="show artist " + textMessage)
    tracks_button = types.InlineKeyboardButton(text="Найти похожие треки", callback_data="show track " + textMessage)
    add_button = types.InlineKeyboardButton(text="Добавить в поиск еще один трек", callback_data="add " + textMessage)
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

    photoFlag = int(getUserSetting(call.message.chat.id, 'show_photo'))
    urlFlag = int(getUserSetting(call.message.chat.id, 'show_url'))

    print("photoFlag = " + str(getUserSetting(call.message.chat.id, 'show_photo')))
    print("urlFlag = " + str(getUserSetting(call.message.chat.id, 'show_url')))

    print("photoFlag = " + str(photoFlag))
    print("urlFlag = " + str(urlFlag))

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
            mess2send = user_out_dict[call.message.chat.id][i].name + " \n"
            if urlFlag:
                mess2send += user_out_dict[call.message.chat.id][i].url
            bot.send_message(call.message.chat.id, mess2send, disable_web_page_preview=True)

            if photoFlag:
                bot.send_photo(call.message.chat.id, user_out_dict[call.message.chat.id][i].image)
    elif method == "track":
        for i in range(0, num_items):
            print(user_out_dict[call.message.chat.id][i].artist)
            print(user_out_dict[call.message.chat.id][i].name)
            print(user_out_dict[call.message.chat.id][i].image)
            print(user_out_dict[call.message.chat.id][i].url)
            print()
            mess2send = user_out_dict[call.message.chat.id][i].artist + " - " + user_out_dict[call.message.chat.id][i].name + " \n"
            if urlFlag:
                mess2send += user_out_dict[call.message.chat.id][i].url
            bot.send_message(call.message.chat.id, mess2send, disable_web_page_preview=True)

            if photoFlag:
                bot.send_photo(call.message.chat.id, user_out_dict[call.message.chat.id][i].image)
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

