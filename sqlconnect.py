
import mysql.connector
import DatetimeConverter as dt



def MysqlConfig():
    mysqlconfig = {
        "host": "plowmantelemetrydb.clsmeutacd1v.eu-west-2.rds.amazonaws.com",
        "user": "admin",
        "password": "bR0m3lIad2021!!",
        "database": "plowmantelemetryschema",
    }
    return mysqlconfig

def sqlGetLogin(username):
    config = MysqlConfig()
    mydb = mysql.connector.connect(**config)
    cursor = mydb.cursor()
    query = "SELECT * FROM plowmantelemetryschema.PBL_Telemetry_UserAccess;"
    cursor.execute(
        query,
    )
    for x in cursor:
        return "".join(x)

def GetTableByID(name):
    config = MysqlConfig()
    mydb = mysql.connector.connect(**config)
    cursor = mydb.cursor()
    query = "SELECT PrimaryTable FROM plowmantelemetryschema.PBL_Telemetry_UserAccess WHERE UserID = %s;"  # AND `Box Number` = %s;") #construct query
    val = cursor.execute(query, (name,))
    for x in cursor:
        return "".join(x)

def InsertSQL(value, table):
    config = MysqlConfig()
    mydb = mysql.connector.connect(**config)
    mycursor = mydb.cursor()
    # sql = "INSERT INTO `plowmantelemetryschema`.`PBL_Telemetry` (`Box Number`, `DateTime`, `Longitude`, `Latitude`, `Temperature 1`) VALUES ('\'PBL v0.4.2', '2021-10-06 08:03:29', '54.08095', '-1.1727', '13')"
    sql = (
        "INSERT INTO plowmantelemetryschema."
        + table
        + " (`Box Number`, `DateTime`, `Latitude`, `Longitude`, `T1`,`T2`,`T3`,`T4`,`T5`,`T6`,`T7`,`T8`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    )
    examples = ("PBL v0.4.1", "2021-10-06 08:03:29", "54.08095", "-1.1727", "-127.000")
    print(value)
    value = value.lstrip('"')
    value = value.rstrip('"')
    value = eval(value)
    print(value)
    mycursor.execute(sql, value)
    mydb.commit()

def SelectSQL(table):
    config = MysqlConfig()
    mydb = mysql.connector.connect(**config)
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT * FROM `plowmantelemetryschema`." + table + " ORDER BY ID DESC;"
    )
    myresult = mycursor.fetchall()

    data = []
    for x in myresult:
        data.append(x)
        data.append("\\n\\n")
    return data

def sqlGetTemperaturesForGraph(boxNumber,dateTime,timeRange, filename):
    config = MysqlConfig()
    mydb = mysql.connector.connect(**config)
    TemperatureID = "T1"
    cursor = mydb.cursor()  # define cursor
    query = "SELECT DateTime,T1,T2,T3,T4,T5,T6,T7,T8 FROM PBL_Uploaded_Data WHERE `Box Number` = %s AND DateTime BETWEEN %s AND %s ORDER BY DateTime;"  # AND `Box Number` = %s;") #construct query
    cursor.execute(
        query,
        (
            boxNumber,
            timeRange,
            dateTime,
        ),
    )  # execute query using time range and box number
    # define array
    ID = []
    T1 = []
    T2 = []
    T3 = []
    T4 = []
    T5 = []
    T6 = []
    T7 = []
    T8 = []

    for (
        Identifier,
        Temp1,
        Temp2,
        Temp3,
        Temp4,
        Temp5,
        Temp6,
        Temp7,
        Temp8,
    ) in cursor:  # loop through each row and store longitude and latitude under cursor
        if Temp1 != -127 and Temp1 != 85:
            T1.append(Temp1)
        else:
            T1.append(float("NaN"))
        if Temp2 != -127 and Temp2 != 85:
            T2.append(Temp2)
        else:
            T2.append(float("NaN"))
        if Temp3 != -127 and Temp3 != 85:
            T3.append(Temp3)
        else:
            T3.append(float("NaN"))
        if Temp4 != -127 and Temp4 != 85:
            T4.append(Temp4)
        else:
            T4.append(float("NaN"))
        if Temp5 != -127 and Temp5 != 85:
            T5.append(Temp5)
        else:
            T5.append(float("NaN"))
        if Temp6 != -127 and Temp6 != 85:
            T6.append(Temp6)
        else:
            T6.append(float("NaN"))
        if Temp7 != -127 and Temp7 != 85:
            T7.append(Temp7)
        else:
            T7.append(float("NaN"))
        if Temp8 != -127 and Temp8 != 85:
            T8.append(Temp8)
        else:
            T8.append(float("NaN"))
        ID.append(Identifier)
    if not T1:
        return
    
    return T1,T2,T3,T4,T5,T6,T7,T8,ID

# Queries SQL database and finds last row for specified box number. Converts to date or checks if online/offline
# boxNumber = string that is specific to livestock box. e.g. 'PBL v0.4.9' no checks if this is wrong!
# **kwargs:
#          - dateformat. if set as true, will return last packet in format of DD/MM/YYYY HH:MM:SS
#          - status.     if set as true, will return last packet in readable format AND ONLINE/OFFLINE (used on html)
# returns datetime in format of '%Y-%m-%d %H:%M:%S' as standard.
def LastPacketTime(boxNumber, **kwargs):
    config = MysqlConfig()
    mydb = mysql.connector.connect(**config)
    cursor = mydb.cursor()  # define cursor
    query = "SELECT DateTime, Latitude, Longitude FROM PBL_Uploaded_Data WHERE  `Box Number` = %s ORDER BY DateTime DESC LIMIT 1  ;"  # construct query
    cursor.execute(query, (boxNumber,))
    for result in cursor:
        result = list(result)
        if kwargs.get("dateformat"):  # probably will be unused
            readableDate = dt.ConvertToReadableTime((result[0]))
            return readableDate
        if kwargs.get("status"):  # if we want to check ONLINE/OFFLINE
            readableDate = dt.ConvertToReadableTime((result[0]))
            if dt.PacketAge(
                5, result[0]
            ):  # Pass in 20 minutes, we can expose and change this later
                result[0] = readableDate + " || ONLINE "
            else:
                result[0] = readableDate + " || OFFLINE "
            return result
        else:
            return result



def GetAllBoxNumbers():
    config = MysqlConfig()
    mydb = mysql.connector.connect(**config)
    cursor = mydb.cursor()
    query = "SELECT BoxNumber FROM PBL_Telemetry_Summary;"
    cursor.execute(query)
    livestockBoxes = []
    for BoxNumber in cursor:
        livestockBoxes.append(BoxNumber[0])
    return livestockBoxes

def GetAllUsersBoxes(emailAddress):
    config = MysqlConfig()
    mydb = mysql.connector.connect(**config)
    cursor = mydb.cursor()
    cursor.execute("SELECT BoxID FROM plowmantelemetryschema.PBL_User_Boxes WHERE UserEmail = '%s';" % (emailAddress))
    userBoxes = []
    for result in cursor:
        userBoxes.append(result[0])
    return userBoxes

