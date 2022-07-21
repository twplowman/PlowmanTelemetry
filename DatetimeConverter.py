from datetime import datetime, timedelta



def PacketAge(timeMinutes, dateTime):
    '''
    compares date (in a datetime format of '%Y-%m-%d %H:%M:%S') against current server time.
    timeMinutes = integer time in minutes
    dateTime = time to evaluate (e.g. last packet from sql server)
    returns true or false based upon defined allowable range in minutes.
    '''
    difference = (datetime.utcnow() - dateTime) - timedelta(minutes=timeMinutes)
    # print(difference)
    if difference < timedelta(0):
        return True
    else:
        return False



def ConvertToDateTime(readableDate):
    '''
    Converts readable format into datetime type.
    '%d/%m/%Y %H:%M:%S' to '%Y-%m-%d %H:%M:%S'
    readableDate = date time in format of DD/MM/YYYY HH:MM:SS (e.g. time from picos)
    returns dateTime = datetime in format of YYYY-MM-DD HH/MM/SS (e.g. datetime from sql server)
    '''
    dateTime = datetime.strptime(readableDate, "%Y-%m-%d %H:%M:%S")
    return dateTime


def ConvertToReadableTime(dateTime):
    '''
    Converts datetime into more readable format
    '%Y-%m-%d %H:%M:%S' to '%d/%m/%Y %H:%M:%S'
    dateTime = date time in format of YYYY-MM-DD HH/MM/SS (e.g. datetime from sql server)
    returns readableDate
    '''
    readableDate = datetime.strftime(dateTime, "%d/%m/%Y %H:%M:%S")
    return readableDate

def GetTodaysDate(hour = 0, minute=0, second=0, microsecond = 0):
    ''' 
    Returns todays date in the format YYYY-MM-DD HH:MM:SS
    Standard returns todays date at 00:00:00
    Optional Parameters for hour, minute, second and microsecond
    '''
    dateTime = datetime.utcnow().replace(hour=hour, minute=minute, second=second, microsecond=microsecond).strftime("%Y-%m-%d %H:%M:%S")
    return dateTime
