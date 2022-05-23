
from passlib.hash import sha256_crypt

import sqlconnect as sql
import mysql.connector

def CheckUsernameInDatabase(username):
    config = sql.MysqlConfig()
    mydb = mysql.connector.connect(**config)
    cursor = mydb.cursor()
    cursor.execute("SELECT Username FROM plowmantelemetryschema.PBL_Telemetry_UserAccess WHERE Username = '%s'" % (username))
    response = cursor.fetchall()
    if len(response) == 0 :
        return
    else:
        return response[0][0]

def CheckEmailInDatabase(emailAddress):
    config = sql.MysqlConfig()
    mydb = mysql.connector.connect(**config)
    cursor = mydb.cursor()
    cursor.execute("SELECT Email FROM plowmantelemetryschema.PBL_Telemetry_UserAccess WHERE Email = '%s'" % (emailAddress))
    response = cursor.fetchall()
    if len(response) == 0 :
        return
    else:
        return response[0][0]

def CreateAccount(emailAddress, username, password,firstName,lastName):
    passwordToStore = sha256_crypt.hash(password)
    print(passwordToStore)
    
    if CheckUsernameInDatabase(username) is not None:
        print("Username is already in database")
        return False
    if CheckEmailInDatabase(emailAddress) is not None:
        print("Email is already in database")
        return False

    try:
        config = sql.MysqlConfig()
        mydb = mysql.connector.connect(**config)
        mycursor = mydb.cursor()
        data = (
            "INSERT INTO plowmantelemetryschema.PBL_Telemetry_UserAccess (`Email`,`Username`,`Password`,`FirstName`,`LastName`,`AccessLevel`) VALUES (%s,%s,%s,%s,%s,'User')"
        )
        mycursor.execute(data, (emailAddress,username,passwordToStore,firstName,lastName))
        mydb.commit()
        return True
    except:
        return False
    finally:
       pass
    

def GetPassword(loginMethod,loginValue):
    '''
    Choice to get Password via Email Address or Username
    # Options
    If 'loginMethod' is 1, Email Address is used
    If 'loginMethod' is 2, Username is used
    '''
    # we assume the email address is in the database. 
    config = sql.MysqlConfig()
    mydb = mysql.connector.connect(**config)
    cursor = mydb.cursor()
    if loginMethod == 1: #Email Address
        cursor.execute("SELECT Password FROM plowmantelemetryschema.PBL_Telemetry_UserAccess WHERE Email = '%s'" % (loginValue))
    if loginMethod == 2: #Username
        cursor.execute("SELECT Password FROM plowmantelemetryschema.PBL_Telemetry_UserAccess WHERE Username = '%s'" % (loginValue))
    response = cursor.fetchall()
    if len(response) == 0 :
        return
    else:
        return response[0][0]


def GetUserID(loginValue):
    config = sql.MysqlConfig()
    mydb = mysql.connector.connect(**config)
    cursor = mydb.cursor()
    if CheckEmailInDatabase(loginValue) is not None:
        cursor.execute("SELECT UserID FROM plowmantelemetryschema.PBL_Telemetry_UserAccess WHERE Email = '%s'" % (loginValue))
    if CheckUsernameInDatabase(loginValue) is not None:
        cursor.execute("SELECT UserID FROM plowmantelemetryschema.PBL_Telemetry_UserAccess WHERE Username = '%s'" % (loginValue))
    response = cursor.fetchall()
    if len(response) == 0 :
        return
    else:
        return response[0][0]


def Login(loginValue,password):
    
    if CheckEmailInDatabase(loginValue) is not None:
        passwordfromDB = GetPassword(1,loginValue)
        if sha256_crypt.verify(password,passwordfromDB):
            return True
        else:
            return False 

    if CheckUsernameInDatabase(loginValue) is not None:
        passwordfromDB = GetPassword(2,loginValue)   
        if sha256_crypt.verify(password,passwordfromDB):
            return True
        else:
            return False 
    
    print("Email or Username not in Database")
    return False
    


#print(CheckUsernameInDatabase("PBL002"))
#CreateAccount("tom.plowman@me.comc","dexterwatson","bR0m3lIad2022!!")
Login("tom.plowman@me.comc","bR0m3lIad202dasfaf2!!")