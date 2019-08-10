import time
from datetime import datetime


def timeTrans(stamp):
    datatime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(str(stamp)[0:10])))
    datatime = datatime+'.'+str(stamp)[10:]
    return datatime


def isWeekend(date):
    day = datetime.strptime(date[0:16], '%Y-%m-%d %H:%M').weekday()

    if day <= 4:
        return 0
    else:
        return 1

