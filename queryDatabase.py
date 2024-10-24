import mysql.connector as mysql
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to database
snomedDB = mysql.connect(
    host="localhost",
    user=os.getenv("MYSQL_USERNAME"),
    password=os.getenv("MYSQL_PASSWORD"),
    database="snomedct"
)

cursor = snomedDB.cursor()

cursor.execute("SELECT * FROM concept LIMIT 10")
result = cursor.fetchall()

for x in result:
    print(x)
