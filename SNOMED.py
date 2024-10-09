#TODO evaluation with confusion matrix, precision matrix
from urllib.request import urlopen, Request
from urllib.parse import quote
import json
import matplotlib.pyplot as plt
import networkx as nx
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL
import regex as re
from visualizeOwls import visualize_owl
from helperFunctions import getChildrenById, getSnomedConceptId, getParentsById, getConceptById
# Note to self: maybe treat like a shortest route algorithm?

baseUrl = 'https://browser.ihtsdotools.org/snowstorm/snomed-ct'
edition = 'MAIN/SNOMEDCT-NL'
version = '2024-09-30'

# IMPORTANT! You must update this user agent to avoid having your IP banned for 24 hours.
# Replace with a contact email so that we can contact you if your script causes excessive load on the public server
# For example: user_agent = 'example@example.com'
user_agent = 'tienvoortheorie@gmail.com'



def buildOntology(concept_list: str, tree: list, depth: int, ex, g):
    """
    This method is a recursive method generating an ontology. It explores all the children and generates an OWL ontology from this.

    root_concept is the first concept that starts the generation
    tree is the generated concept tree up until now
    depth is the maximum depth of the tree
    ex is the Namespace of the OWL graph
    g is the graph 
    """
    # TODO: work with ID
    # TODO: implement shortest path between concept 1 (Head) and concept 2 (Ear)
    # TODO: why does it not work for the concept head? - because it worked with "Entire head (body structure)" - we should use head structure
    if not concept_list:
        print(f"Concept '{concept_list}' not found.")
        return
    if depth == 0:
        g.serialize(destination='head_ontology.ttl', format='turtle')
        print("OWL ontology created successfully!")
        return tree
    
    # Get the parents of the current concept
    new_tree = getParentsById(conceptId=concept_list)
    if new_tree:
        # Add the new_tree to the main tree
        tree.extend(new_tree)
        print(tree)
        
        # Recursively build for each child
        for index in range(len(new_tree)):
            g = add_OWL_class(new_tree[index], g, ex, concept_list[1])
            buildOntology(new_tree[index], tree, depth - 1, ex, g)

    return tree
def BFS_ontology(graph, start, search_term):
    queue = [start]
    visited = [start]

    while len(queue) > 0:
        current = queue.pop(0)
        parents = getParentsById(current, search_term)
        if parents == True:
            print(f"Start word with ID '{start}' has a partOf relationship with {search_term}")
            queue = []
            break
        for parent in parents:
            if parent not in visited:
                queue.append(parent)
                visited.append(parent)
                print(visited)

def add_OWL_class(conc, g, ex, main_class):
    concept = sanitize_uri(conc)
    main_class = sanitize_uri(main_class)
    subclass = URIRef(ex[concept])
    main_class = URIRef(ex[main_class])
    g.add((subclass, RDF.type, OWL.Class))
    g.add((subclass, RDFS.subClassOf, main_class))
    g.add((subclass, RDFS.label, Literal(conc)))
    return g

def sanitize_uri(name):
    # Replace spaces with underscores and remove any invalid characters
    sanitized_name = re.sub(r'\s+', '_', name)  # Replace spaces with underscores
    sanitized_name = re.sub(r'[^a-zA-Z0-9_]', '', sanitized_name)  # Remove invalid characters
    return sanitized_name

def buildOWL(input_dict, guideline_title, debug = True):
    conc = sanitize_uri(guideline_title)
    ex = Namespace(f"http://example.org/{conc}#")
    g = Graph()
    # Ontology Declaration
    g.bind("ex", ex)  # Bind the custom namespace for easier access
    g.add((URIRef(f"http://example.org/{conc}"), RDF.type, OWL.Ontology))

    main_class_name = sanitize_uri(guideline_title)
    main_class = URIRef(ex[main_class_name])
    g.add((main_class, RDF.type, OWL.Class))
    g.add((main_class, RDFS.label, Literal(guideline_title)))

    if not debug: 
        identify_root_IDs(input_dict)
    else: 
        input_dict = {'ear': ['117590005', 'Ear structure (body structure)', ['ear', 'ear structure']], 
                      'head': ['302548004', 'Entire head (body structure)', ['head', 'head structure']]}

    for key, items in input_dict.items():
        #TODO: search term is alles behalve het element nu
        BFS_ontology([],items[0], search_term = "head")
        #buildOntology(items[0], [], 6, ex, g)

def most_common(lst):
    return max(set(lst), key=lst.count)

def identify_root_IDs(input_dict: dict):
    #We loop through the synonyms, gather all IDs and check the one that is most occuring
    for key, value in input_dict.items():
        ID_set = []
        ID_set.append(getSnomedConceptId(key))
        for synonym in value[2]:
            ID_set.append(getSnomedConceptId(synonym))
        value[0] = most_common(ID_set)
        value[1] = getConceptById(value[0])
    return input_dict

dictionary = {
    'ear':['ID', "prefered label", ['ear', 'ear structure']],
    'head': ['ID', "prefered label",['head', 'head structure']], 
    #'External Auditory Canal': ['ID', "prefered label",['External Auditory Canal']],
    #'Eardrum': ['ID', "prefered label",['eardrum']]
}
buildOWL(dictionary, "Otitis Externa")

#a: findings (symptomen)/disorders opzoeken in snomed - body parts die je nog niet hebt toevoegen\

#1: scrapen NHG 
#2: identificeren van concepten (chatGPT) - 'dictionary' maken
#3: ID identificeren (API call?) + dubbele verwijderen - voor alles ID toevoegen
#4: DFS of !BFS! op parents - keyword matching: omhoog totdat we vinden dat head een parent is
#5: relatie toekennen (isPartOf)
#6: repeat
#7: patient relatie voor overblijven

#8: titel richtlijn richtlijn toevoegen en linken aan symptomen + patient
#visualize_owl(file_name = "generalized_ontology.ttl")
#visualize_owl(file_name = "otitis_externa_ontology.ttl")