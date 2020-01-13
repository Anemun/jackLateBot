# В этом файле идёт обработка коллбэков

import databaseProvider
from texttable import Texttable
from datetime import datetime

# Получить числа недели из номера недели
def getWeekDaysByWeekNumber(week: int):
    currentYear = datetime.isocalendar(datetime.now())[0]
    firstday = datetime.strptime("{0}-W{1}-1".format(currentYear, week), "%Y-W%W-%w")
    lastday = datetime.strptime("{0}-W{1}-0".format(currentYear, week), "%Y-W%W-%w")
    result = "{0} - {1}".format(firstday.strftime("%d.%m.%Y"), lastday.strftime("%d.%m.%Y"))
    return result

def statMy(callArgs, callUserId, callUsername):
    reply = ""
    calldataArgs = str.split(callArgs, '-')

    if calldataArgs[0] == "currentMonth":
        month = str(datetime.now().month)
        if len(month) == 1:                          # datetime.now().month возвращает месяц без ведущего нуля. Надо скорректировать.
            month = '0{0}'.format(month)
        result = databaseProvider.getResultForUser(userId=callUserId, month=month)
        reply = "Cтатистика по пользователю {0} за месяц {4}:\n\n" \
                "Минут переработок: {1}\n" \
                "Минут опозданий: {2}\n" \
                "ИТОГО:  {3} минут" \
                .format(callUsername, result[0], result[1], result[2], month)           

    elif calldataArgs[0] == "month":
        month = calldataArgs[1]        
        result = databaseProvider.getResultForUser(userId=callUserId, month=month)
        reply = "Cтатистика по пользователю {0} за месяц {4}:\n\n" \
                "Минут переработок: {1}\n" \
                "Минут опозданий: {2}\n" \
                "ИТОГО:  {3} минут"\
                .format(callUsername, result[0], result[1], result[2], month)

    elif calldataArgs[0] == "full":
        result = databaseProvider.getResultForUser(userId=callUserId, full=True, month="00")
        reply = "Полная статистика по пользователю {0}:\n\n" \
                "Минут переработок: {1}\n" \
                "Минут опозданий: {2}\n" \
                "ИТОГО:  {3} минут"\
                .format(callUsername, result[0], result[1], result[2])
               
    return reply


def statUser(callArgs):
    reply = ""
    calldataArgs = str.split(callArgs, '-')

    if calldataArgs[0] == "currentMonth":
        month = str(datetime.now().month)
        if len(month) == 1:                          # datetime.now().month возвращает месяц без ведущего нуля. Надо скорректировать.
            month = '0{0}'.format(month)
        userName = calldataArgs[1]
        userId = databaseProvider.getUserIdByUsername(userName)[0]
        result = databaseProvider.getResultForUser(userId=userId, month=month)
        reply = "Cтатистика по пользователю {0} за месяц {4}:\n\n" \
                "Минут переработок: {1}\n" \
                "Минут опозданий: {2}\n" \
                "ИТОГО:  {3} минут" \
                .format(userName, result[0], result[1], result[2], month)

    elif calldataArgs[0] == "month":
        month = calldataArgs[1]
        userName = calldataArgs[2]
        userId = databaseProvider.getUserIdByUsername(userName)[0]        
        result = databaseProvider.getResultForUser(userId=userId, month=month)
        reply = "Cтатистика по пользователю {0} за месяц {4}:\n\n" \
                "Минут переработок: {1}\n" \
                "Минут опозданий: {2}\n" \
                "ИТОГО:  {3} минут"\
                .format(userName, result[0], result[1], result[2], month)

    elif calldataArgs[0] == "full":
        userName = calldataArgs[1]
        userId = databaseProvider.getUserIdByUsername(userName)[0]
        result = databaseProvider.getResultForUser(userId=userId, full=True, month="00")
        reply = "Полная статистика по пользователю {0}:\n\n" \
                "Минут переработок: {1}\n" \
                "Минут опозданий: {2}\n" \
                "ИТОГО:  {3} минут"\
                .format(userName, result[0], result[1], result[2])

    return reply


def statAllUsers(callArgs):
    reply = ""
    calldataArgs = str.split(callArgs, '-')

    if calldataArgs[0] == "currentMonth":
        month = str(datetime.now().month)
        if len(month) == 1:                          # datetime.now().month возвращает месяц без ведущего нуля. Надо скорректировать.
            month = '0{0}'.format(month)
        stat = databaseProvider.getResultAllUsers(month=month)

        reply = "<pre>Статистика по всем пользователям за месяц {0}:\n".format(month)
        table = Texttable()
        table.set_deco(Texttable.BORDER | Texttable.HEADER)
        table.set_header_align(["c", "c", "c", "c"])
        table.header(["СОТРУДНИК", "ПЕРЕР.", "ОПОЗД.", "ИТОГО"])
        for i in range(0, len(stat)):
            userStat = stat[i]
            table.add_row([userStat[3], userStat[0], userStat[1], userStat[2]])
        reply += table.draw() 
        reply +="</pre>"

    elif calldataArgs[0] == "full":
        month = str(datetime.now().month)
        if len(month) == 1:                          # datetime.now().month возвращает месяц без ведущего нуля. Надо скорректировать.
            month = '0{0}'.format(month)
        stat = databaseProvider.getResultAllUsers(month="00", full=True)
        reply = "<pre>Статистика по всем пользователям за всё время:\n"
        table = Texttable()
        table.set_deco(Texttable.BORDER | Texttable.HEADER)
        table.set_header_align(["c", "c", "c", "c"])
        table.header(["СОТРУДНИК", "ПЕРЕР.", "ОПОЗД.", "ИТОГО"])
        for i in range(0, len(stat)):
            userStat = stat[i]
            table.add_row([userStat[3], userStat[0], userStat[1], userStat[2]])
        reply += table.draw() 
        reply +="</pre>"

    elif calldataArgs[0] == "lastWeek":
        lastWeek = datetime.isocalendar(datetime.now())[1] - 1
        if lastWeek < 1:
            reply = "ОШИБКА. К сожалению, информация за прошлый год недоступна в таком виде."
        stat = databaseProvider.getResultAllUsersByWeek(str(lastWeek))
        reply = "Статистика по всем пользователям за предыдущую неделю ({0}):\n" \
                "Формат: пользователь;переработки;опоздания;итог\n".format(getWeekDaysByWeekNumber(lastWeek))
        for i in range(0, len(stat)):
            userStat = stat[i]
            reply += "\n{0};{1};{2};{3}" \
                      .format(userStat[3], userStat[0], userStat[1], userStat[2])

    elif calldataArgs[0] == "currentWeek":
        currentWeek = datetime.isocalendar(datetime.now())[1]
        if currentWeek < 1:
            reply = "ОШИБКА. К сожалению, информация за прошлый год недоступна в таком виде."
        stat = databaseProvider.getResultAllUsersByWeek(str(currentWeek))
        reply = "Статистика по всем пользователям за текущую неделю ({0}):\n" \
                "Формат: пользователь;переработки;опоздания;итог\n".format(getWeekDaysByWeekNumber(currentWeek))
        for i in range(0, len(stat)):
            userStat = stat[i]
            reply += "\n{0};{1};{2};{3}" \
                      .format(userStat[3], userStat[0], userStat[1], userStat[2])

    elif calldataArgs[0] == "month":
        month = calldataArgs[1]
        if len(month) == 1:                          # datetime.now().month возвращает месяц без ведущего нуля. Надо скорректировать.
            month = '0{0}'.format(month)
        stat = databaseProvider.getResultAllUsers(month=month)
        reply = "<pre>Статистика по всем пользователям за месяц {0}:\n".format(month)
        table = Texttable()
        table.set_deco(Texttable.BORDER | Texttable.HEADER)
        table.set_header_align(["c", "c", "c", "c"])
        table.header(["СОТРУДНИК", "ПЕРЕР.", "ОПОЗД.", "ИТОГО"])
        for i in range(0, len(stat)):
            userStat = stat[i]
            table.add_row([userStat[3], userStat[0], userStat[1], userStat[2]])
        reply += table.draw() 
        reply +="</pre>"

    return reply


def listUserRecords(callArgs):
    reply = ""
    calldataArgs = str.split(callArgs, '-')

    if calldataArgs[0] == "currentMonth":
        month = str(datetime.now().month)
        if len(month) == 1:                          # datetime.now().month возвращает месяц без ведущего нуля. Надо скорректировать.
            month = '0{0}'.format(month)
        userName = calldataArgs[1]
        userId = databaseProvider.getUserIdByUsername(userName)[0]
        result = databaseProvider.getResultListByType(userId=userId, month=month)
        
        replyWork = "Переработки пользователя {0} за месяц {1}:\n\n".format(userName, month)
        resultWork = result[0]
        for i in range(0, len(resultWork)):
            userRecord = resultWork[i]
            replyWork += "\n{0}; +{1}; \"{2}\"".format(userRecord[0], userRecord[1], userRecord[2])
        
        replyLate = "Опоздания пользователя {0} за месяц {1}:\n\n".format(userName, month)
        resultLate = result[1]
        for i in range(0, len(resultLate)):
            userRecord = resultLate[i]
            replyLate += "\n{0}; -{1}; \"{2}\"".format(userRecord[0], userRecord[1], userRecord[2])        
        

    elif calldataArgs[0] == "month":
        month = calldataArgs[1]
        if len(month) == 1:                          # datetime.now().month возвращает месяц без ведущего нуля. Надо скорректировать.
            month = '0{0}'.format(month)
        userName = calldataArgs[2]
        userId = databaseProvider.getUserIdByUsername(userName)[0]
        result = databaseProvider.getResultListByType(userId=userId, month=month)
        
        replyWork = "Переработки пользователя {0} за месяц {1}:\n\n".format(userName, month)
        resultWork = result[0]
        for i in range(0, len(resultWork)):
            userRecord = resultWork[i]
            replyWork += "\n{0}; +{1}; \"{2}\"".format(userRecord[0], userRecord[1], userRecord[2])
        
        replyLate = "Опоздания пользователя {0} за месяц {1}:\n\n".format(userName, month)
        resultLate = result[1]
        for i in range(0, len(resultLate)):
            userRecord = resultLate[i]
            replyLate += "\n{0}; -{1}; \"{2}\"".format(userRecord[0], userRecord[1], userRecord[2])        

    return (replyWork, replyLate)