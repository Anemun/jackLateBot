# Файл взаимодействия с базой данных

import sqlite3
from datetime import datetime

currentYear = str(datetime.now().year)
databaseFilePath = ""

def init(databaseName, year):
    global databaseFilePath, currentYear
    databaseFilePath = databaseName
    currentYear = year
    createTableIfNotExist()

def createTableIfNotExist():    
    conn = sqlite3.connect(databaseFilePath)
    cursor = conn.cursor()

    # создаём таблицу юзеров
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS [users] ('
        '[Id] integer PRIMARY KEY NOT NULL, '
        '[userId] string, '
        '[username] string,'
        '[firstName] string,'
        '[lastName] string);')

    # таблицу с записями о переработках/опозданиях
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS [times] ('
        '[Id] integer PRIMARY KEY NOT NULL, '
        '[userId] string,'
        '[date] datetime,'
        '[type] string,'
        '[time] integer,'
        '[comment] string);')

    # и таблицу истории записей
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS [history] ('
        '[Id] integer PRIMARY KEY NOT NULL, '
        '[username] string,'
        '[date] datetime, '
        '[message] string);')

    conn.commit()
    conn.close()


def getUsersList():
    dbResult = runQuery("SELECT username FROM users ORDER BY username")
    result = []
    for i in range(0, len(dbResult)):
        result.append(dbResult[i][0])
    return result


def getUsersWithNames():
    dbResult = runQuery("SELECT username,firstName,lastName FROM users")
    return dbResult


# запись в базу. Переписать, тут что-то неправильно
def writeToDatabase(user, date, late:int=0, work: int =0, comment: str =""):
    if late > 0:
        runQuery("INSERT INTO times (userId, date, type, time, comment) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')"
                 .format(user, date, "late", late, comment))
    elif work > 0:
        runQuery("INSERT INTO times (userId, date, type, time, comment) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')"
                 .format(user, date, "work", work, comment))


# запись истории в базу истории
def writeHistory(username, date, message):
    runQuery("INSERT INTO history (username, date, message) VALUES ('{0}', '{1}', '{2}')".format(username, date, message))


# получить историю
def getHistory():    
    result = runQuery("SELECT date, username, message FROM history ORDER BY Id DESC LIMIT 50")    
    return result


# Получить итоговую статистику конкретного пользователя
def getResultForUser(userId: int, month: str, full: bool = False):
    if full is True:
        late = runQuery("SELECT sum(time) FROM times WHERE type='late' AND userId='{0}'".format(userId))
        work = runQuery("SELECT sum(time) FROM times WHERE type='work' AND userId='{0}'".format(userId))
    else:
        late = runQuery(
            "SELECT sum(time) FROM times "
            "WHERE type='late' "
            "AND userId='{0}' "
            "AND strftime('%m', date) = '{1}' "
            "AND strftime('%Y', date) = '{2}'"
            .format(userId, month, currentYear))
        work = runQuery(
            "SELECT sum(time) FROM times "
            "WHERE type='work' "
            "AND userId='{0}' "
            "AND strftime('%m', date) = '{1}' "
            "AND strftime('%Y', date) = '{2}'"
            .format(userId, month, currentYear))

    late = late[0][0]
    if late is None:
        late = 0
    work = work[0][0]
    if work is None:
        work = 0
    result = (int(work), int(late), int(work) - int(late))
    return result


def getResultAllUsers(month: str, full: bool = False):
    stat = []
    users = getUsersList()
    for i in range(0, len(users)):
        userId = getUserIdByUsername(users[i])[0]
        if full is True:
            late = runQuery("SELECT sum(time) FROM times WHERE type='late' AND userId='{0}'".format(userId))
            work = runQuery("SELECT sum(time) FROM times WHERE type='work' AND userId='{0}'".format(userId))
        else:
            late = runQuery(
                "SELECT sum(time) FROM times "
                "WHERE type='late' "
                "AND userId='{0}' "
                "AND strftime('%m', date) = '{1}'"
                "AND strftime('%Y', date) = '{2}'"
                .format(userId, month, currentYear))
            work = runQuery(
                "SELECT sum(time) FROM times "
                "WHERE type='work' "
                "AND userId='{0}' "
                "AND strftime('%m', date) = '{1}'"
                "AND strftime('%Y', date) = '{2}'"
                .format(userId, month, currentYear))
        late = late[0][0]
        if late is None:
            late = 0
        work = work[0][0]
        if work is None:
            work = 0
        result = (int(work), int(late), int(work) - int(late), users[i])
        stat.append(result)
    return stat


def getResultAllUsersByWeek(week: str):
    stat = []
    users = getUsersList()
    for i in range(0, len(users)):
        userId = getUserIdByUsername(users[i])[0]
        late = runQuery(
            "SELECT sum(time) FROM times "
            "WHERE type='late' "
            "AND userId='{0}' "
            "AND strftime('%W', date) = '{1}'"
            "AND strftime('%Y', date) = '{2}'"
            .format(userId, week, currentYear))
        work = runQuery(
            "SELECT sum(time) FROM times "
            "WHERE type='work' "
            "AND userId='{0}' "
            "AND strftime('%W', date) = '{1}'"
            "AND strftime('%Y', date) = '{2}'"
            .format(userId, week, currentYear))
        late = late[0][0]
        if late is None:
            late = 0
        work = work[0][0]
        if work is None:
            work = 0
        result = (int(work), int(late), int(work) - int(late), users[i])
        stat.append(result)
    return stat


def getResultListByType(userId: int, month: str):
    resultWork = runQuery(
        "SELECT date,time,comment FROM times "
        "WHERE strftime('%m', date) = '{0}' "
        "AND strftime('%Y', date) = '{1}' "
        "AND type = 'work' "
        "AND userId = '{2}'"
        "ORDER BY date ASC"
        .format(month, currentYear, userId))
    resultLate = runQuery(
        "SELECT date,time,comment FROM times "
        "WHERE strftime('%m', date) = '{0}' "
        "AND strftime('%Y', date) = '{1}' "
        "AND type = 'late' "        
        "AND userId = '{2}'"
        "ORDER BY date ASC"
        .format(month, currentYear, userId))
    return (resultWork,resultLate)


def consolidateDatabase(date):
    users = getUsersList()
    for i in range(0, len(users)):
        userId = getUserIdByUsername(users[i])[0]
        late=work=0
        work = runQuery(
            "SELECT sum(time) FROM times "            
            "WHERE userId='{0}'"
            "AND type = 'work' "            
            .format(userId))[0][0]
        late = runQuery(
            "SELECT sum(time) FROM times "            
            "WHERE userId='{0}'"
            "AND type = 'late' "            
            .format(userId))[0][0]
        if late == None: late = 0
        if work == None: work = 0
        timeSum = work-late
        runQuery(
            "DELETE from times "
            "WHERE userId='{0}'"
            .format(userId))

        if timeSum > 0:
            runQuery("INSERT INTO times (userId, date, type, time, comment) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')"
                    .format(userId, date, "work", timeSum, "Консолидация времени"))
        elif timeSum < 0:
            runQuery("INSERT INTO times (userId, date, type, time, comment) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')"
                    .format(userId, date, "late", timeSum*(-1), "Консолидация времени"))


def getUserIdByUsername(username):
    result = runQuery("SELECT userId FROM users WHERE username = '{0}'".format(username))
    return result[0]


# Проверяем, существует ли такой юзер
def isUserExist(user):
    conn = sqlite3.connect(databaseFilePath)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = '{0}'".format(user))
    result = cursor.fetchone()
    conn.close()

    if result:
        return True
    else:
        return False


# Вносим нового пользователя в базу
def registerUser(userId, username, firstName, lastName):
    runQuery("INSERT INTO users (userId, username, firstName, lastName) VALUES ('{0}', '{1}', '{2}', '{3}')"
             .format(userId, username, firstName, lastName))


# выполнить запрос к БД
def runQuery(query):
    conn = sqlite3.connect(databaseFilePath)
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result
