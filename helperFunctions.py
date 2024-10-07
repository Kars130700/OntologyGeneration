from urllib.request import urlopen, Request
from urllib.parse import quote
import json
import matplotlib.pyplot as plt
import networkx as nx
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL
import regex as re
from visualizeOwls import visualize_owl
# Note to self: maybe treat like a shortest route algorithm?

baseUrl = 'https://browser.ihtsdotools.org/snowstorm/snomed-ct'
edition = 'MAIN/SNOMEDCT-NL'
version = '2024-09-30'

# IMPORTANT! You must update this user agent to avoid having your IP banned for 24 hours.
# Replace with a contact email so that we can contact you if your script causes excessive load on the public server
# For example: user_agent = 'example@example.com'
user_agent = 'tienvoortheorie@gmail.com'

def urlopen_with_header(url):
    # adds User-Agent header otherwise urlopen on its own gets an IP blocked response
    req = Request(url)
    req.add_header('User-Agent', user_agent)
    return urlopen(req)

#Prints fsn of a concept
def getConceptById(id):
    url = baseUrl + '/browser/' + edition + '/' + version + '/concepts/' + id
    response = urlopen_with_header(url).read()
    data = json.loads(response.decode('utf-8'))

    print (data['fsn']['term'])

#Prints description by id
def getDescriptionById(id):
    url = baseUrl + '/' + edition + '/' + version + '/descriptions/' + id
    response = urlopen_with_header(url).read()
    data = json.loads(response.decode('utf-8'))

    print (data['term'])

#Prints number of concepts with descriptions containing the search term
def getConceptsByString(searchTerm):
    url = baseUrl + '/browser/' + edition + '/' + version + '/concepts?term=' + quote(searchTerm) + '&activeFilter=true&offset=0&limit=50'
    response = urlopen_with_header(url).read()
    data = json.loads(response.decode('utf-8'))

    print (data['total'])

#Prints number of descriptions containing the search term with a specific semantic tag
def getDescriptionsByStringFromProcedure(searchTerm, semanticTag):
    url = baseUrl + '/browser/' + edition + '/' + version + '/descriptions?term=' + quote(searchTerm) + '&conceptActive=true&semanticTag=' + quote(semanticTag) + '&groupByConcept=false&searchMode=STANDARD&offset=0&limit=50'
    response = urlopen_with_header(url).read()
    data = json.loads(response.decode('utf-8'))

    print (data['totalElements'])
    
 #Prints snomed code for searched disease or symptom
def getSnomedCodeSimilar(searchTerm):
    url = baseUrl + '/browser/' + edition + '/' + version + '/descriptions?term=' + quote(searchTerm) + '&conceptActive=true&groupByConcept=false&searchMode=STANDARD&offset=0&limit=50'
    response = urlopen_with_header(url).read()
    data = json.loads(response.decode('utf-8'))

    for term in data['items']:
      if searchTerm in term['term']:
        print("{} : {}".format(term['term'], term['concept']['conceptId']))
 
def getSnomedCode(searchTerm):
    url = baseUrl + '/browser/' + edition + '/' + version + '/descriptions?term=' + quote(searchTerm) + '&conceptActive=true&groupByConcept=false&searchMode=STANDARD&offset=0&limit=50'
    response = urlopen_with_header(url).read()
    data = json.loads(response.decode('utf-8'))

    for term in data['items']:
      if searchTerm == term['term']:
        print("{} : {}".format(term['term'], term['concept']['conceptId']))

# Get parents of a concept
def getParentsById(conceptId, limit=8):
    url = f"{baseUrl}/browser/{edition}/{version}/concepts/{conceptId}/parents?offset=0&limit={limit}"
    response = urlopen_with_header(url).read()
    data = json.loads(response.decode('utf-8'))

    parents = []
    print(data)
    # for item in data['items']:
    #     parents.append({'id': item['conceptId'], 'term': item['fsn']['term']})
    
    return parents

# Get children of a concept
def getChildrenById(conceptId, limit=3, depth = 5):
    print(conceptId)
    url = f"{baseUrl}/browser/{edition}/{version}/concepts/{conceptId}/children?offset=0&limit={limit}"
    response = urlopen_with_header(url).read()
    data = json.loads(response.decode('utf-8'))
    children = []
    print(data)
    for child in data:
        concept_id = child.get("conceptId")
        fsn = child.get("fsn", {}).get("term")
        pt = child.get("pt", {}).get("term")
        children.append(pt)

    return children

# Helper function to get a SNOMED concept by name and return the ID
def getSnomedConceptId(searchTerm):
    url = f"{baseUrl}/browser/{edition}/{version}/descriptions?term={quote(searchTerm)}&conceptActive=true&groupByConcept=false&searchMode=STANDARD&offset=0&limit=50"
    response = urlopen_with_header(url).read()
    data = json.loads(response.decode('utf-8'))

    for term in data['items']:
        if searchTerm.lower() == term['term'].lower():
            return term['concept']['conceptId']

    return None
