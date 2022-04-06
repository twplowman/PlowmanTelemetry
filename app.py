from distutils.command.config import config
import re
from flask import Flask,jsonify, session, redirect, render_template , url_for, request
import mysql.connector
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os
import mplleaflet
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

def MysqlConfig():
        mysqlconfig = {
                'host':'plowmantelemetrydb.clsmeutacd1v.eu-west-2.rds.amazonaws.com',
                'user':'admin',
                'password':'bR0m3lIad2021!!',
                'database':'plowmantelemetryschema'
                }
        return mysqlconfig

def sqlGetLogin(username):
        config = MysqlConfig()
        mydb = mysql.connector.connect(**config)
        cursor = mydb.cursor()
        query = ("SELECT * FROM plowmantelemetryschema.PBL_Telemetry_UserAccess;")
        cursor.execute(query,)
        for x in cursor:
                return ''.join(x)

def CheckUsernameInDatabase(username):
        config = MysqlConfig()
        mydb = mysql.connector.connect(**config)
        cursor = mydb.cursor()
        query = ("SELECT * FROM plowmantelemetryschema.PBL_Telemetry_UserAccess WHERE UserID = %s;")
        cursor.execute(query,(username,))
        for x in cursor:
                return ''.join(x)

def GetTableByID(name):
        config = MysqlConfig()
        mydb = mysql.connector.connect(**config)
        cursor = mydb.cursor()
        query = ("SELECT PrimaryTable FROM plowmantelemetryschema.PBL_Telemetry_UserAccess WHERE UserID = %s;") #AND `Box Number` = %s;") #construct query
        val = cursor.execute(query,(name,))
        for x in cursor:
                return ''.join(x)


def InsertSQL(value,table):
        config = MysqlConfig()
        mydb = mysql.connector.connect(**config)
        mycursor = mydb.cursor()
        #sql = "INSERT INTO `plowmantelemetryschema`.`PBL_Telemetry` (`Box Number`, `DateTime`, `Longitude`, `Latitude`, `Temperature 1`) VALUES ('\'PBL v0.4.2', '2021-10-06 08:03:29', '54.08095', '-1.1727', '13')"
        sql = "INSERT INTO plowmantelemetryschema." + table + " (`Box Number`, `DateTime`, `Latitude`, `Longitude`, `T1`,`T2`,`T3`,`T4`,`T5`,`T6`,`T7`,`T8`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        examples = ('PBL v0.4.1','2021-10-06 08:03:29','54.08095','-1.1727','-127.000')
        print(value)
        value = value.lstrip('\"')
        value = value.rstrip('\"')
        value = eval(value)
        print(value)
        mycursor.execute(sql,value)
        mydb.commit()


def SelectSQL(table):
        config = MysqlConfig()
        mydb = mysql.connector.connect(**config)
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM `plowmantelemetryschema`." + table + " ORDER BY ID DESC;")
        myresult = mycursor.fetchall()
    
        data = []
        for x in myresult:
                data.append(x)
                data.append('\\n\\n')
        return (data)


    
# Creates a Map based upon dateTime and boxNumber from SQL database
# Uses SQL database: plowmantelemetryschema.PBL_Telemetry_2
# Finds latitude and longitude in range and plots these on a map
# TODO - add a few days before? or all day ranges.
# Saves file to same place this code executes then file is moved to correct folder
#
# dateTime = datetime in format of YYYY-MM-DD HH/MM/SS 
# boxNumber = string that is specific to livestock box. e.g. 'PBL v0.4.9' no checks if this is wrong!
# filename = name to save map (usually same as box number)
def sqlOneDayMap(table, dateTime, timeRange,filename):
    
	config = MysqlConfig()
	mydb = mysql.connector.connect(**config)
	cursor = mydb.cursor() #define cursor
	query = ("SELECT latitude, longitude FROM ") + table + (" WHERE DateTime BETWEEN %s AND %s;") #AND `Box Number` = %s;") #construct query
	cursor.execute(query,(timeRange,dateTime,)) #execute query using time range and box number
	#query = ("SELECT Latitude,Longitude FROM plowmantelemetryschema.PBL_Telemetry_0_5_3 WHERE DateTime > '2021-11-30 09:00:00' AND `Box Number` = 'PBL001';")
	#cursor.execute(query)
	#define arrays
	print(dateTime,timeRange)
	latitudeRange = []
	longitudeRange = []
	for (latitude, longitude) in cursor: #loop through each row and store longitude and latitude under cursor
		latitudeRange.append(latitude)
		longitudeRange.append(longitude)
	if not latitudeRange:
		return
	plt.plot(longitudeRange,latitudeRange,color = '#0e4a99',lw=4) #plot graph - wants to be in own function.
	plt.scatter(longitude,latitude,s=200,alpha=0.8,c='g')
	mplleaflet.save_html(fileobj=filename) #save map to same place as this function
	os.system("mv "+ filename+" ~/flaskapp/static/maps/") #move to correct folder so server can find the file
	plt.clf()




# Creates a Temperature graph based upon dateTime and boxNumber from SQL database
# Uses SQL database: plowmantelemetryschema.PBL_Telemetry_2
# Finds temperature and ID in range and plots these on a graph
# TODO - add a few days before? or all day ranges.
# Saves file to same place this code executes then file is moved to correct folder
#
# dateTime = datetime in format of YYYY-MM-DD HH/MM/SS 
# boxNumber = string that is specific to livestock box. e.g. 'PBL v0.4.9' no checks if this is wrong!
# filename = name to save temperature (usually same as box number)
def sqlGenerateTempGraph(table,dateTime, timeRange,filename):
	config = MysqlConfig()
	mydb = mysql.connector.connect(**config)
	TemperatureID = "T1"
	cursor = mydb.cursor() #define cursor
	query = ("SELECT DateTime,T1,T2,T3,T4,T5,T6,T7,T8 FROM ") + table + (" WHERE DateTime BETWEEN %s AND %s;") #AND `Box Number` = %s;") #construct query
	cursor.execute(query,(timeRange,dateTime,)) #execute query using time range and box number
	#define array
	ID = []
	T1 = []
	T2 = []
	T3 = []
	T4 = []
	T5 = []
	T6 = []
	T7 = []
	T8 = []

	for (Identifier, Temp1, Temp2, Temp3, Temp4, Temp5, Temp6, Temp7, Temp8) in cursor: #loop through each row and store longitude and latitude under cursor
		if Temp1 != -127 and Temp1 != 85:
			T1.append(Temp1)
		else :
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

	plt.plot(ID,T1,ID,T2,ID,T3,ID,T4,ID,T5,ID,T6,ID,T7,ID,T8) #plot graph - wants to be in own function.
	plt.xticks(rotation=45)
	plt.grid()
	plt.title("Livestock Internal Temperature")
	plt.xlabel("Time || days/hrs")
	plt.ylabel("Temperature ˚C")
	plt.savefig(filename, bbox_inches='tight')
	os.system("mv "+ filename+" ~/flaskapp/static/maps/") #move to correct folder so server can find the file
	plt.clf() 
    

# Queries SQL database and finds last row for specified box number. Converts to date or checks if online/offline 
# boxNumber = string that is specific to livestock box. e.g. 'PBL v0.4.9' no checks if this is wrong!
# **kwargs:
#          - dateformat. if set as true, will return last packet in format of DD/MM/YYYY HH:MM:SS
#          - status.     if set as true, will return last packet in readable format AND ONLINE/OFFLINE (used on html)
# returns datetime in format of '%Y-%m-%d %H:%M:%S' as standard. 
def LastPacketTime(table,boxNumber,**kwargs):
	config = MysqlConfig()
	mydb = mysql.connector.connect(**config)
	cursor = mydb.cursor() #define cursor
	query = ("SELECT DateTime FROM ")+table+(" WHERE  `Box Number` = %s ORDER BY DateTime DESC LIMIT 1  ;") #construct query
	cursor.execute(query,(boxNumber,))
	for datetime in cursor:
		if kwargs.get('dateformat'): #probably will be unused
			readableDate = ConvertToReadableTime((datetime[0]))
			return readableDate
		if kwargs.get('status'): #if we want to check ONLINE/OFFLINE
			readableDate = ConvertToReadableTime((datetime[0]))
			if PacketAge(100,datetime[0]): #Pass in 20 minutes, we can expose and change this later
				readableDate = readableDate + " || ONLINE "
			else:
				readableDate = readableDate + " || OFFLINE "
			return readableDate
		else:
			return datetime[0]

# compares date (in a datetime format of '%Y-%m-%d %H:%M:%S') against current server time.
# timeMinutes = integer time in minutes 
# dateTime = time to evaluate (e.g. last packet from sql server)
# returns true or false based upon defined allowable range in minutes.
def PacketAge(timeMinutes,dateTime): 
    difference = (datetime.utcnow() - dateTime) - timedelta(minutes = timeMinutes)
    #print(difference)
    if difference < timedelta(0):
        return True
    else:
        return False
    
# Converts readable format into datetime type.
# '%d/%m/%Y %H:%M:%S' to '%Y-%m-%d %H:%M:%S'
# readableDate = date time in format of DD/MM/YYYY HH:MM:SS (e.g. time from picos)
# returns dateTime = datetime in format of YYYY-MM-DD HH/MM/SS (e.g. datetime from sql server)
def ConvertToDateTime(readableDate):
    dateTime = datetime.strptime(readableDate, '%Y-%m-%d %H:%M:%S')
    return dateTime

# Converts datetime into more readable format
# '%Y-%m-%d %H:%M:%S' to '%d/%m/%Y %H:%M:%S'
# dateTime = date time in format of YYYY-MM-DD HH/MM/SS (e.g. datetime from sql server)
# returns readableDate
def ConvertToReadableTime(dateTime):
    readableDate = datetime.strftime(dateTime, '%d/%m/%Y %H:%M:%S')
    return readableDate


def GetSummaryDetails(table):
	config = MysqlConfig()
	mydb = mysql.connector.connect(**config)
	cursor = mydb.cursor() #define cursor
	query = ("SELECT TotalDistance, WeeklyDistance, Customer, CustomerBoxNumber, LastPacketDistance FROM PBL_Telemetry_Summary WHERE PBL_Telemetry_Summary.Table = %s;")
	cursor.execute(query,(table,))
	result = []
	for (TotalDistance, WeeklyDistance, Customer, CustomerBoxNumber, LastPacketDistance) in cursor:
		result = [TotalDistance, WeeklyDistance, Customer, CustomerBoxNumber, LastPacketDistance]
	return result


# Queries the database for specific data related to chosen livestock box
# Last Packet
# Temperature
def GetCurrentAverageTemperature(table,boxNumber):
	config = MysqlConfig()
	mydb = mysql.connector.connect(**config)
	cursor = mydb.cursor() #define cursor
	query = ("SELECT T1,T2,T3,T4,T5,T6,T7,T8 FROM ")+table+(" WHERE  `Box Number` = %s ORDER BY DateTime DESC LIMIT 1  ;") #construct query
	cursor.execute(query,(boxNumber,))
	data = 0
	for (x) in cursor:
		i = 0
		counter = 0
		while i<8:
			if x[i] != -127 and x[i] != 85:
				data = data + x[i]
				counter = counter + 1
			i = i + 1   
		data = round(data/counter,1)    
	return data








@app.route('/')
def index():
    if 'username' in session:
        username = session.get('username')
        return redirect(url_for('boxRoute',name = username))
    return redirect(url_for('login'))


#Endpoint for JMW Farms Box #001    
@app.route('/post/tplowman',methods=['GET','POST'])
def sqlTPlowman():
    table = "PBL_Telemetry_TPlowman"
    if request.method == 'POST':
        input_json = request.get_json(force=True)
        #print('data:',input_json)
        value = input_json['value']
        
        InsertSQL(value,table)
        #Save to sql
        return value
    if request.method == 'GET':
        values = SelectSQL(table)
        return jsonify(values)    

#Endpoint for Redpath Box #001    
@app.route('/post/Redpath',methods=['GET','POST'])
def sqlRedpath():
    table = "PBL_Telemetry_Redpath"
    if request.method == 'POST':
        input_json = request.get_json(force=True)
        #print('data:',input_json)
        value = input_json['value']
        
        InsertSQL(value,table)
        #Save to sql
        return value
    if request.method == 'GET':
        values = SelectSQL(table)
        return jsonify(values)   


@app.route("/mysql/<username>")
def sqlLogin(username):
        username = sqlGetLogin(username)
        return jsonify(username)

@app.route("/render")
def rendertemplate():
        return render_template('base.html')


@app.route('/box/redirect')
def BoxRedirect():
    if request.method == 'GET':
        if 'username' not in session:
            return redirect(url_for('login'))
        username = session.get('username')
        return redirect(url_for('boxRoute', name=username))

@app.route('/box/<string:name>',methods=['GET','POST'])   
def boxRoute(name):
    if request.method == 'GET':
        if 'username' not in session:
            return redirect(url_for('login'))
        
        if session.get('username') != name:
            return redirect(url_for('AccessDenied'))

        # Defining table to query
        table = GetTableByID(name)
        boxNumber = name
        
        #Getting datetime
        dateTimeOneDay = datetime.utcnow() - timedelta(days = 30)
        dateTime = dateTimeOneDay.strftime('%Y-%m-%d %H:%M:%S')
        dateTimeNow = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        #calculating graphs
        #sqlOneDayMap(table,dateTimeNow,dateTime,boxNumber+".html")
        sqlGenerateTempGraph(table,dateTimeNow,dateTime,boxNumber+".png")
        
        #get general details
        summaryDetails = GetSummaryDetails(table)
        
        templateData = {
            'mapHTML': boxNumber,
            'currentTemperature': GetCurrentAverageTemperature(table,boxNumber),
            'totalDistance': round(summaryDetails[0]),
            'weeklyDistance': round(summaryDetails[1]),
            'lastPacket': LastPacketTime(table,boxNumber,status = True),
            'customer': summaryDetails[2],
            'customerBoxNumber': summaryDetails[3],
            'lastPacketDistance': round(summaryDetails[4],2),
            'latitude': '',
            'longitude': '',
            'sensorsOnline': '',
            'fanUptime': '',
            'location': ''
        }
        return render_template('CustomerView.html', **templateData)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        username = session.get('username')

        if CheckUsernameInDatabase(username) is None:
            return redirect(url_for('AccessDenied'))

        return redirect(url_for('boxRoute',name = username))
    if 'username' in session:
        session.pop('username',None)
        username = 'Logged Out'
    else:
        username = 'Not Logged In'
    return render_template('login_page.html',username=username)

@app.route('/formtest',methods=['GET','POST'])
def formtest():
    return "hello"

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/accessDenied')
def AccessDenied():
    return "Access Denied"



from werkzeug.debug import DebuggedApplication
app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

app.debug = False


if __name__ == "__main__":
        app.run(host='0.0.0.0')



