import email
from flask import Flask, jsonify, session, redirect, render_template, url_for, request
import mysql.connector
from datetime import datetime, timedelta


import sqlconnect as sql
import maps as maps
import LivestockBoxes as box
import UserAccess

app = Flask(__name__)
app.secret_key = "A0Zr98j/3yX R~XHH!jmN]LWX/,?RT"

# Queries SQL database and finds last row for specified box number. Converts to date or checks if online/offline
# boxNumber = string that is specific to livestock box. e.g. 'PBL v0.4.9' no checks if this is wrong!
# **kwargs:
#          - dateformat. if set as true, will return last packet in format of DD/MM/YYYY HH:MM:SS
#          - status.     if set as true, will return last packet in readable format AND ONLINE/OFFLINE (used on html)
# returns datetime in format of '%Y-%m-%d %H:%M:%S' as standard.
def LastPacketTime(boxNumber, **kwargs):
    config = sql.MysqlConfig()
    mydb = mysql.connector.connect(**config)
    cursor = mydb.cursor()  # define cursor
    query = "SELECT DateTime, Latitude, Longitude FROM PBL_Uploaded_Data WHERE  `Box Number` = %s ORDER BY DateTime DESC LIMIT 1  ;"  # construct query
    cursor.execute(query, (boxNumber,))
    for result in cursor:
        result = list(result)
        if kwargs.get("dateformat"):  # probably will be unused
            readableDate = ConvertToReadableTime((result[0]))
            return readableDate
        if kwargs.get("status"):  # if we want to check ONLINE/OFFLINE
            readableDate = ConvertToReadableTime((result[0]))
            if PacketAge(
                5, result[0]
            ):  # Pass in 20 minutes, we can expose and change this later
                result[0] = readableDate + " || ONLINE "
            else:
                result[0] = readableDate + " || OFFLINE "
            return result
        else:
            return result

# compares date (in a datetime format of '%Y-%m-%d %H:%M:%S') against current server time.
# timeMinutes = integer time in minutes
# dateTime = time to evaluate (e.g. last packet from sql server)
# returns true or false based upon defined allowable range in minutes.
def PacketAge(timeMinutes, dateTime):
    difference = (datetime.utcnow() - dateTime) - timedelta(minutes=timeMinutes)
    # print(difference)
    if difference < timedelta(0):
        return True
    else:
        return False


# Converts readable format into datetime type.
# '%d/%m/%Y %H:%M:%S' to '%Y-%m-%d %H:%M:%S'
# readableDate = date time in format of DD/MM/YYYY HH:MM:SS (e.g. time from picos)
# returns dateTime = datetime in format of YYYY-MM-DD HH/MM/SS (e.g. datetime from sql server)
def ConvertToDateTime(readableDate):
    dateTime = datetime.strptime(readableDate, "%Y-%m-%d %H:%M:%S")
    return dateTime


# Converts datetime into more readable format
# '%Y-%m-%d %H:%M:%S' to '%d/%m/%Y %H:%M:%S'
# dateTime = date time in format of YYYY-MM-DD HH/MM/SS (e.g. datetime from sql server)
# returns readableDate
def ConvertToReadableTime(dateTime):
    readableDate = datetime.strftime(dateTime, "%d/%m/%Y %H:%M:%S")
    return readableDate



def GetAllBoxNumbers():
    config = sql.MysqlConfig()
    mydb = mysql.connector.connect(**config)
    cursor = mydb.cursor()
    query = "SELECT BoxNumber FROM PBL_Telemetry_Summary;"
    cursor.execute(query)
    livestockBoxes = []
    for BoxNumber in cursor:
        livestockBoxes.append(BoxNumber[0])
    return livestockBoxes




def CheckUsernameInSession(name):
    if "username" not in session:
        return False
    sessionUsername = (session.get("username"))
    if sessionUsername != name:
        return redirect(url_for("boxRoute"))


@app.route("/")
def index():
    if "username" in session:
        username = session.get("username")
        return redirect(url_for("boxRoute"))
    return redirect(url_for("login",response="Please login"))



# Endpoint for JMW Farms Box #001
@app.route("/post/tplowman", methods=["GET", "POST"])
def sqlTPlowman():
    table = "PBL_Telemetry_TPlowman"
    if request.method == "POST":
        input_json = request.get_json(force=True)
        # print('data:',input_json)
        value = input_json["value"]

        sql.InsertSQL(value, table)
        # Save to sql
        return value
    if request.method == "GET":
        values = sql.SelectSQL(table)
        return jsonify(values)


# Endpoint for Redpath Box #001
@app.route("/post/Redpath", methods=["GET", "POST"])
def sqlRedpath():
    table = "PBL_Telemetry_Redpath"
    if request.method == "POST":
        input_json = request.get_json(force=True)
        # print('data:',input_json)
        value = input_json["value"]

        sql.InsertSQL(value, table)
        # Save to sql
        return value
    if request.method == "GET":
        values = sql.SelectSQL(table)
        return jsonify(values)


@app.route("/mysql/<username>")
def sqlLogin(username):
    username = sql.sqlGetLogin(username)
    return jsonify(username)


@app.route("/render")
def rendertemplate():
    return render_template("base.html")


@app.route("/box/redirect")
def BoxRedirect():
    if request.method == "GET":
        if "username" not in session:
            return redirect(url_for("login",response="Please login"))
        username = session.get("username")
        return redirect(url_for("boxRoute"))


@app.route("/Summary")
def summary():
    
    #work out number of columns in summary table
    livestockBoxes = GetAllBoxNumbers()
    #get summary details
    print(livestockBoxes)
    summaryDetails = [["TotalDistance, WeeklyDistance, Customer, CustomerBoxNumber,LastPacketDistance,SensorsOnline,Average Temperature"]]
    for BoxNumber in livestockBoxes:
        lastPacket = LastPacketTime(BoxNumber, status=True)
        if lastPacket is None:
            lastPacket = [0,0,0]
        print(lastPacket)
        summaryDetails.append([box.GetSummaryDetails(BoxNumber),box.GetCurrentAverageTemperature(BoxNumber),maps.LatLonNamedLocation(lastPacket[1],lastPacket[2])]) 
        print (summaryDetails)
    print (summaryDetails)
    
    return jsonify(summaryDetails)


@app.route("/updateSessionData", methods = ["POST"])
def UpdateSessionData():
    CheckUsernameInSession()

    

@app.route("/live-tracking", methods=["GET", "POST"])
def boxRoute():
    if CheckUsernameInSession(session.get("username")) is False:
        return redirect(url_for("login"))

    if request.method == "POST":

        # Form Data from Datepicker
        dateTimeStart = request.form.get('startDate')
        dateTimeEnd = request.form.get('endDate')
        session["dateTimeStart"] = request.form.get('startDate')
        session["dateTimeEnd"] = request.form.get('endDate')
        autoRefresh = session.get("autoRefresh")
        if dateTimeStart is None:
            #Ajax updating session values. 
            updateType = request.form.get("updateType")
            data = (request.get_json())
            print(type(data))
            data = (request.get_json(force=True))
            updateType = data['updateType']

            #something is wrong here
            if updateType == "Ajax":
                dateTimeStart = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
                dateTimeEnd = datetime.utcnow().replace(hour=23, minute=59, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
                session["dateTimeStart"] = dateTimeStart
                session["dateTimeEnd"] = dateTimeEnd
                session["autoRefresh"] = request.form.get('autoRefresh') #think this is done client side at the moment
                
            #return jsonify(request.form)
    if request.method == "GET":
        dateTimeStart = session.get("dateTimeStart")
        dateTimeEnd = session.get("dateTimeEnd")
        autoRefresh = session.get("autoRefresh")
        

    # defining table to query - We always query the same table now.
    # table = GetTableByID(name)
    boxNumber = session.get("username")
    if boxNumber is None:
            return "Account needs to be associated with correct Livestock box. Please contact Administrator"
    # Getting datetime
    

    # calculating graphs
    # sqlOneDayMap(table,dateTimeEnd,dateTime,boxNumber+".html")
    filename = boxNumber+".html"
    maps.RenderMap(dateTimeEnd,dateTimeStart,boxNumber,filename)
    maps.sqlGenerateTempGraph(boxNumber, dateTimeEnd, dateTimeStart, boxNumber + ".png")

    # get general details
    summaryDetails = box.GetSummaryDetails(boxNumber)
    averageTemperature = box.GetCurrentAverageTemperature(boxNumber)
    averageTemperatureColour = maps.AverageTemperatureColour(averageTemperature)
    print (averageTemperatureColour)

    # get last packet details
    lastPacket = LastPacketTime(boxNumber, status=True)
        
    templateData = {
        "mapHTML": boxNumber,
        "currentTemperature": averageTemperature ,
        "totalDistance": round(summaryDetails[0]),
        "weeklyDistance": round(summaryDetails[1]),
        "lastPacket": lastPacket[0],
        "customer": summaryDetails[2],
        "customerBoxNumber": summaryDetails[3],
        "lastPacketDistance": round(summaryDetails[4], 2),
        "latitude": lastPacket[1],
        "longitude": lastPacket[2],
        "sensorsOnline": summaryDetails[5],
        "fanUptime": "",
        "location": maps.LatLonNamedLocation(lastPacket[1],lastPacket[2]),
        "StartTime" : ConvertToDateTime(dateTimeStart).strftime("%-d %b %y"),
        "StartTimeWD" : ConvertToDateTime(dateTimeStart).strftime("%a"),
        "StartTimeHr":ConvertToDateTime(dateTimeStart).strftime("%-I%p"),
        "EndTime" : ConvertToDateTime(dateTimeEnd).strftime("%-d %b %y"),
        "EndTimeWD" : ConvertToDateTime(dateTimeEnd).strftime("%a"),
        "EndTimeHr":ConvertToDateTime(dateTimeEnd).strftime("%-I%p"),
        "AutoRefresh": autoRefresh,
        "temperatureAverageColour": averageTemperatureColour
    }
    return render_template("CustomerView.html", **templateData)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if UserAccess.Login(username,password) is False:
            return redirect(url_for("login",response="Incorrect Username or Password"))

        # We have now authenticated, so lets get the Box ID (temporary)
        userID = UserAccess.GetUserID(username)
        session["username"] = userID
        if userID is None:
            return "Account needs to be associated with correct Livestock box. Please contact Administrator"

# required format 'YYYY-MM-DD HH:mm:S'
        dateTimeStart = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
        dateTimeEnd = datetime.utcnow().replace(hour=23, minute=59, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
        session["dateTimeStart"] = dateTimeStart
        session["dateTimeEnd"] = dateTimeEnd
        session["autoRefresh"] = "true"
        return redirect(url_for("boxRoute"))
    if "username" in session:
        session.pop("username", None)
        username = "Logged Out"
    else:
        username = "Not Logged In"
    return render_template("login_page.html", response="Please login")

@app.route("/logout")
def logout():
    # remove the username from the session if it's there
    session.pop("username", None)
    return redirect(url_for("index"))


@app.route("/register",  methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if UserAccess.CreateAccount(request.form["email"],request.form["username"],request.form["password"],request.form["firstName"],request.form["lastName"]) is True:
            return "Successfully created account"
        else:
            return "Error creating account"
    if request.method == "GET":
        return render_template("register_page.html")

@app.route("/accessDenied")
def AccessDenied():
    return "Access Denied"


from werkzeug.debug import DebuggedApplication

app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

app.debug = True


if __name__ == "__main__":
    app.run(host="0.0.0.0",port="8080")
   # session.permanent = True    
