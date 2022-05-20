
import mysql.connector



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


def CheckUsernameInDatabase(username):
    config = MysqlConfig()
    mydb = mysql.connector.connect(**config)
    cursor = mydb.cursor()
    query = "SELECT * FROM plowmantelemetryschema.PBL_Telemetry_UserAccess WHERE UserID = %s;"
    cursor.execute(query, (username,))
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