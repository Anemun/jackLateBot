# В этом файле реализуется приём сообщений бота, начальный парсинг и обратная отправка в телеграм

import telebot
import databaseProvider
import argparse, sys
from telebot import types
from datetime import datetime

parser=argparse.ArgumentParser()
parser.add_argument('--botToken', help='telegram bot token')
parser.add_argument('--databasePath', help='pathtoDatabase')
args=parser.parse_args()

TELEGRAM_BOT_TOKEN = args.botToken
DATABASE_FILE = args.databasePath

version = "1.3.0-20200113"

timeFormat = '%Y-%m-%d %H:%M:%S'

command_my = "my-StepA"
command_statUserA = "statUser-StepA"
command_statUserB = "statUser-StepB"
command_statAll = "statAll-StepA"
command_listTimeA = "listTime-StepA"
command_listTimeB = "listTime-StepB"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Создаём начальные таблицы в базе данных, если они не существуют
databaseProvider.init(DATABASE_FILE, str(datetime.now().year))

hideMarkup = types.ReplyKeyboardRemove()


def registerUserIfNotExist(userSender):
    # зарегистрировать пользователя, если его нет в базе
    if not databaseProvider.isUserExist(userSender.username):
        databaseProvider.registerUser(userSender.id, userSender.username, userSender.first_name, userSender.last_name)



# Попросить пользователя зарегистрироваться 
def askUserForRegister(message):
    if databaseProvider.isUserExist(message.from_user.username) is False:
        bot.send_message(text="Вас нет в базе данных, сначала пришлите что-нибудь", chat_id=message.chat.id)
        return


# Обработчик команды /history. Вывод истории записей, кто когда что писал
@bot.message_handler(commands=["history"])
def showHistory(message):
    databaseResult = databaseProvider.getHistory()
    if len(databaseResult) > 0:        
        text = "Последние 100 записей:\n\n"   
        for i in range(len(databaseResult)):
            text += str(databaseResult[i])
            text += "\n"
        bot.send_message(chat_id=message.chat.id,
                         text=text)    


# Обработчик команды /help. Вывод справки
@bot.message_handler(commands=["help"])
def showHelp(message):
    text = 'Если вы опаздываете, пришлите время опоздания со знаком минус ' \
           '(например, опаздывая на 15 минут, пришлите "-15")\n\n' \
           'Если вы перерабатываете или компенсируете опоздание, пришлите время со знаком плюс ' \
           '(например, переработав лишний час, пришлите "+60")\n\n' \
           'Вы можете добавить комментарий через пробел после времени\n' \
           '(например, "-20 пробки") \n\n' \
           'Команды: \n' \
           '/my - показать собственную статистику \n' \
           '/stat - показать статистику другого пользователя\n' \
           '/statall - показать статистику всех пользователей\n' \
           '/listtime - показать все записи пользователя за месяц в разбивке по типу\n ' \
		   '/getusers - Вывести список зарегистрированных пользователей\n '
           
    bot.send_message(chat_id=message.chat.id, text=text)


# Компановка клавиатуры
def createKeyboard(callbackFuncName: str, customArg: str="",
                   full: bool=False, curMonth: bool=False, 
                   lastWeek: bool=False, curWeek:bool=False, 
                   usrButtons: bool=False, monthButtons: bool=False):

    keyboard = types.InlineKeyboardMarkup()
    keyboard.row_width = 2

    if customArg != "":
        customArg = "-{0}".format(customArg)

    if full:
        buttonFull = types.InlineKeyboardButton(text="Полная статистика", callback_data="{0};full{1}".format(callbackFuncName, customArg))
        keyboard.add(buttonFull)

    if curMonth:
        buttonCurMonth = types.InlineKeyboardButton(text="Текущий месяц", callback_data="{0};currentMonth{1}".format(callbackFuncName, customArg))  
        keyboard.add(buttonCurMonth)

    if curWeek:
        buttonCurWeek = types.InlineKeyboardButton(text="Текущая неделя", callback_data="{0};currentWeek{1}".format(callbackFuncName, customArg))  
        keyboard.add(buttonCurWeek)

    if lastWeek:
        buttonLastWeek = types.InlineKeyboardButton(text="Прошлая неделя", callback_data="{0};lastWeek{1}".format(callbackFuncName, customArg))  
        keyboard.add(buttonLastWeek)

    if usrButtons:
        users = databaseProvider.getUsersList()
        for i in range(0, len(users)):
            button = types.InlineKeyboardButton(text=users[i], callback_data="{0};user-{1}".format(callbackFuncName, users[i]))
            keyboard.add(button)

    if monthButtons:
        keyboard.row(types.InlineKeyboardButton(text="01", callback_data="{0};month-01{1}".format(callbackFuncName, customArg)),
                    types.InlineKeyboardButton(text="02", callback_data="{0};month-02{1}".format(callbackFuncName, customArg)),
                    types.InlineKeyboardButton(text="03", callback_data="{0};month-03{1}".format(callbackFuncName, customArg)),
                    types.InlineKeyboardButton(text="04", callback_data="{0};month-04{1}".format(callbackFuncName, customArg)),
                    types.InlineKeyboardButton(text="05", callback_data="{0};month-05{1}".format(callbackFuncName, customArg)),
                    types.InlineKeyboardButton(text="06", callback_data="{0};month-06{1}".format(callbackFuncName, customArg)))
        keyboard.row(types.InlineKeyboardButton(text="07", callback_data="{0};month-07{1}".format(callbackFuncName, customArg)),
                    types.InlineKeyboardButton(text="08", callback_data="{0};month-08{1}".format(callbackFuncName, customArg)),
                    types.InlineKeyboardButton(text="09", callback_data="{0};month-09{1}".format(callbackFuncName, customArg)),
                    types.InlineKeyboardButton(text="10", callback_data="{0};month-10{1}".format(callbackFuncName, customArg)),
                    types.InlineKeyboardButton(text="11", callback_data="{0};month-11{1}".format(callbackFuncName, customArg)),
                    types.InlineKeyboardButton(text="12", callback_data="{0};month-12{1}".format(callbackFuncName, customArg)))    

    return keyboard


# Обработчик команды /my. Вывод собственной статистики пользователя
@bot.message_handler(commands=["my"])
def getMyStats(message):
    askUserForRegister(message)
    keyboard = createKeyboard(command_my, full=True, curMonth=True, monthButtons=True)
    bot.send_message(text="Выберите месяц для отображения статистики", reply_markup=keyboard, chat_id=message.chat.id)


# Обработчик команды /stat. Вывод статистики другого пользователя
@bot.message_handler(commands=["stat"])
def getUserStats(message):
    keyboard = createKeyboard(command_statUserA, usrButtons=True)
    bot.send_message(text="Выберите пользователя", reply_markup=keyboard, chat_id=message.chat.id)


# Обработчик команды /statall. Вывод статистики по всем пользователям
@bot.message_handler(commands=["statall"])
def getAllUsersStats(message):
    keyboard = createKeyboard(callbackFuncName=command_statAll, full=True, curMonth=True, lastWeek=True, curWeek=True, monthButtons=True)
    bot.send_message(text="Выберите месяц для отображения статистики", reply_markup=keyboard, chat_id=message.chat.id)
    

# Обработчик команды /listTime. Вывод всех записей за месяц в разбивке по типу
@bot.message_handler(commands=["listtime"])
def getListTime(message):
    keyboard = createKeyboard(command_listTimeA, usrButtons=True)
    bot.send_message(text="Выберите пользователя", reply_markup=keyboard, chat_id=message.chat.id)   


# Обработчик команды /getusers. Вывод списка зарегистрированных пользователей
@bot.message_handler(commands=["getusers"])
def getUsers(message):
    result = databaseProvider.getUsersWithNames()
    reply = "Список зарегистрированных пользователей:\n"
    for i in range(0, len(result)):
        reply += "\n{0} ({1} {2})".format(result[i][0], result[i][1], result[i][2])
    bot.send_message(chat_id=message.chat.id, text=reply)    

# Консолидация времени
@bot.message_handler(commands=["consolidate"])
def consolidateTimes(message):    
    databaseProvider.consolidateDatabase(date=str(datetime.now().strftime(timeFormat)))
    bot.send_message(chat_id=message.chat.id, text="Консолидация времени запущена") 
    

# Обработка коллбэков с данными
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    import CallbackMethods as cm
    if call.message:
        calldataMethod = str.split(call.data, ';')[0]
        calldataArgs = str.split(call.data, ';')[1]
		
		# Статистика по собственному пользователю
        if calldataMethod == command_my:
            reply = cm.statMy(calldataArgs, call.from_user.id, call.from_user.username)
            if reply == "":
                reply = "Ошибка обработки. Обратитесь к автору бота (method: {0}, args: {1}".format(calldataMethod, calldataArgs)
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.send_message(chat_id=call.message.chat.id, text=reply)

        # Обработка статистики по другому пользователю (по месяцам). Шаг А - юзер уже выбран и надо выбрать месяц
        elif calldataMethod == command_statUserA:
            user = str.split(calldataArgs, '-')[1]
            keyboard = createKeyboard(command_statUserB, full=True, curMonth=True, monthButtons=True, customArg=user)
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.send_message(text="Выберите месяц для отображения статистики пользователя {0}"
                                   .format(user), 
                                   reply_markup=keyboard, chat_id=call.message.chat.id)

        # Вывод статистики по другому пользователю (по месяцам). Шаг Б - юзер и месяц уже выбраны, получаем статистику
        elif calldataMethod == command_statUserB:
            reply = cm.statUser(calldataArgs)
            if reply == "":
                reply = "Ошибка обработки. Обратитесь к автору бота (method: {0}, args: {1}".format(calldataMethod, calldataArgs)
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.send_message(chat_id=call.message.chat.id, text=reply)

        # Вывод статистики по всем пользователям
        elif calldataMethod == command_statAll:
            reply = cm.statAllUsers(calldataArgs)
            if reply == "":
                reply = "Ошибка обработки. Обратитесь к автору бота (method: {0}, args: {1}".format(calldataMethod, calldataArgs)
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.send_message(chat_id=call.message.chat.id, text=reply)
            

        # Обработка запроса на вывод всех записей пользователя за месяц. Шаг А - юзер уже выбран и надо выбрать месяц
        elif calldataMethod == command_listTimeA:
            user = str.split(calldataArgs, '-')[1]
            keyboard = createKeyboard(command_listTimeB, curMonth=True, monthButtons=True, customArg=user)
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.send_message(text="Выберите месяц для отображения записей пользователя {0}"
                                   .format(user), 
                                   reply_markup=keyboard, chat_id=call.message.chat.id)

        
        # Вывод всех записей пользователя за месяц. Шаг Б - юзер и месяц уже выбраны, получаем статистику
        elif calldataMethod == command_listTimeB:
            reply = cm.listUserRecords(calldataArgs)
            if reply == "":
                reply = "Ошибка обработки. Обратитесь к автору бота (method: {0}, args: {1}".format(calldataMethod, calldataArgs)
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.send_message(chat_id=call.message.chat.id, text=reply[0])
            bot.send_message(chat_id=call.message.chat.id, text=reply[1])


# Обработчик сообщения в телеграме, где есть символ "+"
@bot.message_handler(regexp='\+')
def writeTimePlus(message):
    arrayOfWords = str.split(message.text, ' ')
    timeValue = None
    timeIndex = None
    for i in range(0, len(arrayOfWords)):
        try:
            timeValue = int(str.split(arrayOfWords[i], '+')[1])
            timeIndex = i
        except:
            pass        
    if timeValue == None or timeIndex == None:
        bot.send_message(chat_id=message.chat.id,
                         text="Ошибка обработки. Выберите команду /help для справки по использованию бота")
        return
    else:
        comment = ""
        for n in range(0, len(arrayOfWords)):
            if n != timeIndex:
                comment = comment + ' ' + arrayOfWords[n]
    
    # регистрируем пользователя, если его нет в базе
    registerUserIfNotExist(message.from_user)

    # пишем в базу
    userId = message.from_user.id
    username = message.from_user.username
    databaseProvider.writeToDatabase(user=userId,
                                     date=str(datetime.now().strftime(timeFormat)),
                                     work=int(timeValue),
                                     comment=comment)
    databaseProvider.writeHistory(username=username,
                                  date=str(datetime.now().strftime(timeFormat)),
                                  message=message.text)
    result = "{0}: +{1} к рабочему дню".format(username, timeValue)

    # возвращаем результат пользователю
    bot.send_message(chat_id=message.chat.id, text=result)


# Обработчик сообщения в телеграме, где есть символ "-"
@bot.message_handler(regexp='\-')
def writeTimeMinus(message):
    arrayOfWords = str.split(message.text, ' ')
    timeValue = None
    timeIndex = None
    for i in range(0, len(arrayOfWords)):
        try:
            timeValue = int(str.split(arrayOfWords[i], '-')[1])
            timeIndex = i
        except:
            pass        
    if timeValue == None or timeIndex == None:
        bot.send_message(chat_id=message.chat.id,
                         text="Ошибка обработки. Выберите команду /help для справки по использованию бота")
        return
    else:
        comment = ""
        for n in range(0, len(arrayOfWords)):
            if n != timeIndex:
                comment = comment + ' ' + arrayOfWords[n]

    # регистрируем пользователя, если его нет в базе
    registerUserIfNotExist(message.from_user)

    # пишем в базу
    userId = message.from_user.id
    username = message.from_user.username
    databaseProvider.writeToDatabase(user=userId,
                                     date=str(datetime.now().strftime(timeFormat)),
                                     late=int(timeValue),
                                     comment=comment)
    databaseProvider.writeHistory(username=username,
                                  date=str(datetime.now().strftime(timeFormat)),
                                  message=message.text)
    result = "{0}: -{1} к рабочему дню".format(username, timeValue)

    # возвращаем результат пользователю
    bot.send_message(chat_id=message.chat.id, text=result)
   

@bot.message_handler(commands=["ver"])
def getVersion(message):
    reply = "текущая версия: {0}".format(version)
    bot.send_message(chat_id=message.chat.id, text=reply)

# это постоянное прослушивание сообщений, чтобы запускать обработчики выше. Должно быть В САМОМ КОНЦЕ ФАЙЛА
if __name__ == '__main__':
    bot.polling(none_stop=True)

