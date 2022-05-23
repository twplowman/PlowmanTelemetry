
import sqlconnect as sql
import mysql.connector


#Creates a Livestock Box Class which stores all data related with it. 
class LivestockBoxes(object):
    """Creates a Livestock Box Class which stores all data related with it. 
    
    # Constant Values
    'sensors' - Number of sensors associated with a box.

    # Required Arguments
    'BoxNumber' - As defined in SQL or login. Used for the other args.
    
    # Kwargs (Live Data)
    'Temperature', 'Latitude', 'Longitude', 'Last Packet'
    """

    sensors = 8
    
    def __init__(self,BoxNumber, **kwargs):
        # Predefine attributes with default values
        self.BoxNumber = BoxNumber
        self.Temperature = 0
        self.Latitude = 0
        self.Longitude = 0
        self.HistoricalData = 0
        self.OtherValues = True

        # get a list of all predefined values directly from __dict__
        allowed_keys = list(self.__dict__.keys())

        # Update __dict__ but only for keys that have been predefined 
        # (silently ignore others)
        self.__dict__.update((key, value) for key, value in kwargs.items() 
                             if key in allowed_keys)

        # To NOT silently ignore rejected keys
        rejected_keys = set(kwargs.keys()) - set(allowed_keys)
        if rejected_keys:
            raise ValueError("Invalid arguments in constructor:{}".format(rejected_keys))


def GetSummaryDetails(boxNumber):
    config = sql.MysqlConfig()
    mydb = mysql.connector.connect(**config)
    cursor = mydb.cursor()  # define cursor
    query = "SELECT TotalDistance, WeeklyDistance, Customer, CustomerBoxNumber, LastPacketDistance, SensorsOnline FROM PBL_Telemetry_Summary WHERE PBL_Telemetry_Summary.BoxNumber = %s;"
    cursor.execute(query, (boxNumber,))
    result = []
    for (
        TotalDistance,
        WeeklyDistance,
        Customer,
        CustomerBoxNumber,
        LastPacketDistance,
        SensorsOnline,
    ) in cursor:
        result = [
            TotalDistance,
            WeeklyDistance,
            Customer,
            CustomerBoxNumber,
            LastPacketDistance,
            SensorsOnline,
        ]
    return result

# Queries the database for specific data related to chosen livestock box
# Last Packet
# Temperature
def GetCurrentAverageTemperature(boxNumber):
    config = sql.MysqlConfig()
    mydb = mysql.connector.connect(**config)
    cursor = mydb.cursor()  # define cursor
    query = "SELECT T1,T2,T3,T4,T5,T6,T7,T8 FROM PBL_Uploaded_Data WHERE  `Box Number` = %s ORDER BY DateTime DESC LIMIT 1  ;"  # construct query
    cursor.execute(query, (boxNumber,))
    data = 0
    for x in cursor:
        i = 0
        counter = 0
        while i < 8:
            if x[i] != -127 and x[i] != 85:
                data = data + x[i]
                counter = counter + 1
            i = i + 1
        data = round(data / counter, 1)
    return data


__version_info__ = 0.1
__version__ = "Intitial Testing Version"

__all__ = [
    'MySQLConnection', 'Connect', 'custom_error_exception',

    # Some useful constants
    'FieldType', 'FieldFlag', 'ClientFlag', 'CharacterSet', 'RefreshOption',
    'HAVE_CEXT',

    # Error handling
    'Error', 'Warning',
    'InterfaceError', 'DatabaseError',
    'NotSupportedError', 'DataError', 'IntegrityError', 'ProgrammingError',
    'OperationalError', 'InternalError',

    # DBAPI PEP 249 required exports
    'connect', 'apilevel', 'threadsafety', 'paramstyle',
    'Date', 'Time', 'Timestamp', 'Binary',
    'DateFromTicks', 'DateFromTicks', 'TimestampFromTicks', 'TimeFromTicks',
    'STRING', 'BINARY', 'NUMBER',
    'DATETIME', 'ROWID',

    # C Extension
    'CMySQLConnection',
    ]

