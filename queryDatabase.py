import mysql.connector as mysql
import os
from helperFunctions import getSnomedConceptId, getParentsById, getConceptById
from dotenv import load_dotenv

load_dotenv()

# Connect to database
snomedDB = mysql.connect(
    host="localhost",
    user=os.getenv("MYSQL_USERNAME"),
    password=os.getenv("MYSQL_PASSWORD"),
    database="snomedct"
)
cursor = snomedDB.cursor(buffered=True)

# Helper function to get a SNOMED concept by name and return the ID, replaces helperFunctions.getSnomedConceptId
def querySnomedConceptId(searchTerm):
    query = f"SELECT conceptId, term FROM description as de WHERE de.active = 1 AND de.term = '{searchTerm}'"
    cursor.execute(query)
    
    for (conceptId, term) in cursor:
        if searchTerm.lower() == term.lower():
            return conceptId

    return None

# Prints fsn of a concept, replaces helperFunction.getConceptById
def queryConceptById(id):
    query = f"SELECT term FROM description as de WHERE de.active = 1 AND de.conceptId = {id} AND de.typeId = 900000000000003001"
    cursor.execute(query)
    return cursor.fetchone()[0]

def queryParentsById(conceptId, search_term, limit=8):
    query = f"SELECT destinationId FROM relationship as re WHERE re.active = 1 AND re.sourceId = {conceptId} AND re.typeId = 116680003 LIMIT {limit}"
    cursor.execute(query)
    result = cursor.fetchall()

    parents = []
    for (destinationId) in result:
        fsn = queryConceptById(destinationId[0])

        for word in search_term:
            if word in fsn:
                return (True, word, destinationId[0])
        parents.append((destinationId[0], fsn))
    return parents
    

# Results: 
## getSnomedConceptId('ear') takes about 2.3 seconds, querySnomedConceptId('oor') takes about 4.4 seconds
### api call is 1.9 times faster

## getConceptById(117590005) takes about 0.85 seconds, queryConceptById(117590005) takes 0 seconds
### db query is infinitely faster

## getParentsById("117590005", ["head"]) takes about 1.333 seconds, queryParentsById("117590005", ["hoofd"]) takes about 0.002 seconds
### db query is 666.5 times faster

## while loop with getParentsById takes about 6.150 seconds to find 'head' as a parent, same while loop with queryParentsById takes about 0.006 seconds to find 'hoofd' as a parent
### db search is 1025 times faster