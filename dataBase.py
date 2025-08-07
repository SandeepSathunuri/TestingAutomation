import pyodbc
 
class DatabaseConnector:
    def __init__(self):
        self.server = "ec2-13-233-217-54.ap-south-1.compute.amazonaws.com"
        self.database = "Murali_QA"
        self.username = "qa_validations"
        self.password = "qa_41nk$AVMT&kryvzl7QZ2Buhwtnk1ds7w4"
        self.connection = None
 
    def connect(self):
        try:
            connection_string = (
                'DRIVER={ODBC Driver 17 for SQL Server};'
                f'SERVER={self.server};'
                f'DATABASE={self.database};'
                f'UID={self.username};'
                f'PWD={self.password};'
                "MARS_Connection=Yes;"
            )
            self.connection = pyodbc.connect(connection_string)
            print("Connection successful!")
            return self.connection
        except Exception as e:
            print("Failed to connect to database:", e)
            return None

    def close_connection(self):
        if self.connection:
            self.connection.close()
            print("Connection closed.")
 
 

def get_db_connection():
    return DatabaseConnector().connect()