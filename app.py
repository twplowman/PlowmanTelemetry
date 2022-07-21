from flask import Flask, jsonify, session, redirect, render_template, url_for, request

import sqlconnect as sql
import maps as maps
import LivestockBoxes as box
import UserAccess
import DatetimeConverter as dt

app = Flask(__name__)
app.secret_key = "A0Zr98j/3yX R~XHH!jmN]LWX/,?RT"




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


@app.route("/summary")
def summary():
    if "username" not in session:
        return redirect(url_for("login",response="Please login"))
    
    emailAddress = session.get("email")

    #check access to Boxes
    userBoxes = sql.GetAllUsersBoxes(emailAddress)
    #work out number of columns in summary table
    livestockBoxes = sql.GetAllBoxNumbers()
    #get summary details
    print(livestockBoxes)
    
    
    result = []
    customer = []
    boxNumber = []
    temperature = []
    location = []
    latitude =[]
    longitude = []
    sensors = []
    packets = []
    
    
    [["TotalDistance, WeeklyDistance, Customer, CustomerBoxNumber,LastPacketDistance,SensorsOnline,Average Temperature"]]
    for BoxNumber in userBoxes:
        lastPacket = sql.LastPacketTime(BoxNumber, status=True)
        summaryDetails = box.GetSummaryDetails(BoxNumber)
        currentAverageTemperature = box.GetCurrentAverageTemperature(BoxNumber)
        currentLocation = maps.LatLonNamedLocation(lastPacket[1],lastPacket[2])
        if lastPacket is None:
            lastPacket = [0,    0,0]
        customer.append(summaryDetails[2])
        boxNumber.append(BoxNumber)
        temperature.append(currentAverageTemperature)
        location.append(currentLocation)
        latitude.append(lastPacket[1])
        longitude.append(lastPacket[2])
        sensors.append(summaryDetails[5])
        packets.append(lastPacket[0])
    
    templateData = {
        "customer": customer,
        "customerBoxNumber": boxNumber,
        "currentTemperature": temperature,
        "latitude": latitude,
        "longitude": longitude,
        "sensorsOnline": sensors,
        "location" : location,
        "lastPacket": packets,
    }


    return render_template("summary.html",len = len(customer), **templateData)

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
                dateTimeStart = dt.GetTodaysDate()
                dateTimeEnd = dt.GetTodaysDate(hour=23,minute=59,second=59)
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
    boxNumber = session.get("userID")
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
    lastPacket = sql.LastPacketTime(boxNumber, status=True)
        
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
        "StartTime" : dt.ConvertToDateTime(dateTimeStart).strftime("%-d %b %y"),
        "StartTimeWD" : dt.ConvertToDateTime(dateTimeStart).strftime("%a"),
        "StartTimeHr":dt.ConvertToDateTime(dateTimeStart).strftime("%-I%p"),
        "EndTime" : dt.ConvertToDateTime(dateTimeEnd).strftime("%-d %b %y"),
        "EndTimeWD" : dt.ConvertToDateTime(dateTimeEnd).strftime("%a"),
        "EndTimeHr": dt.ConvertToDateTime(dateTimeEnd).strftime("%-I%p"),
        "AutoRefresh": autoRefresh,
        "temperatureAverageColour": averageTemperatureColour
    }
    return render_template("CustomerView.html", **templateData)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        loginMethod = request.form["username"] #this could be a username or an email address - we will always use email
        password = request.form["password"]
        userData = UserAccess.Login(loginMethod,password)
        if userData is None:
            return redirect(url_for("login",response="Incorrect Username or Password"))

        # We have now authenticated with either username or email, so lets store the user data in the session
        session["email"] = userData[0]
        session["username"] = userData[1]
        session["userID"] = UserAccess.GetUserID(email=userData[0])
        
        # required format 'YYYY-MM-DD HH:mm:S'
        dateTimeStart = dt.GetTodaysDate()
        dateTimeEnd = dt.GetTodaysDate(hour=23,minute=59,second=59)
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
