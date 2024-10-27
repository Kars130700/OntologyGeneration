#TODO evaluation with confusion matrix, precision matrix
from urllib.request import urlopen, Request
from urllib.parse import quote
import json
import time
import matplotlib.pyplot as plt
import networkx as nx
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL
import regex as re
from visualizeOwls import visualize_owl
from helperFunctions import getSnomedConceptId, getParentsById, getConceptById, getSnomedFindingId
from queryDatabase import querySnomedConceptId, queryParentsById, queryConceptById, queryFindingsFindingsiteById
# Note to self: maybe treat like a shortest route algorithm?

baseUrl = 'https://browser.ihtsdotools.org/snowstorm/snomed-ct'
edition = 'MAIN/SNOMEDCT-NL'
version = '2024-09-30'

# IMPORTANT! You must update this user agent to avoid having your IP banned for 24 hours.
# Replace with a contact email so that we can contact you if your script causes excessive load on the public server
# For example: user_agent = 'example@example.com'
user_agent = 'tienvoortheorie@gmail.com'
version = 'db'

def BFS_ontology(graph, start, search_term):
    print(f"Starting BFS with {start[1]}")
    queue = [start]
    visited = [start]
    parent_found = ()

    while len(queue) > 0:
        current = queue.pop(0)
        if version == 'db':
            parents = queryParentsById(current[0], search_term)
        else:
            parents = getParentsById(current[0], search_term)
        print(parents)

        if len(parents) == 0:
            continue
        if parents[0] == True:
            print(f"Start word with ID '{start[1]}' has a partOf relationship with '{parents[1]}'")
            queue = []
            parent_found = parents
            break
        for parent in parents:
            if parent not in visited:
                queue.append(parent)
                visited.append(parent)

    if (parent_found):
        return (parent_found[1])
    print(f"No parent was found for start word with ID '{start[1]}', setting the parent to 'patient'")
    # Link top level concepts with the patient / body structure class
    return ('patient')

def add_OWL_relation(source_concept, target_concept, g, ex, label, patient):
    # Sanitize the input URIs
    if source_concept[0] is None:
        return g
    
    if target_concept is None:
        target_concept = patient
        
    source_concept = sanitize_uri(source_concept[0])  # First element for URI
    target_concept = sanitize_uri(target_concept)  # First element for URI
    
    source_uri = URIRef(ex[source_concept])
    target_uri = URIRef(ex[target_concept])

    # Ensure the hasRelation property is unique
    base_property = URIRef(ex.hasRelation)
    property_uri = base_property
    count = 1
    
    # Check if the property already exists and create a new unique property if necessary
    while (property_uri, RDF.type, OWL.ObjectProperty) in g:
        count += 1
        property_uri = URIRef(ex[f'hasRelation{count}'])
    
    # Add the new unique relation
    g.add((property_uri, RDF.type, OWL.ObjectProperty))
    g.add((property_uri, RDFS.label, Literal(label)))
    g.add((property_uri, RDFS.domain, source_uri))
    g.add((property_uri, RDFS.range, target_uri))

    return g

def add_OWL_class(conc, g, ex, main_class):
    concept = sanitize_uri(conc[0])
    main_class = sanitize_uri(main_class)
    subclass = URIRef(ex[concept])
    main_class = URIRef(ex[main_class])
    g.add((subclass, RDF.type, OWL.Class))
    g.add((subclass, RDFS.subClassOf, main_class))
    g.add((subclass, RDFS.label, Literal(conc[1])))
    return g

def sanitize_uri(name):
    if (type(name) != str):
        name = str(name)
    # Replace spaces with underscores and remove any invalid characters
    sanitized_name = re.sub(r'\s+', '_', name)  # Replace spaces with underscores
    sanitized_name = re.sub(r'[^a-zA-Z0-9_]', '', sanitized_name)  # Remove invalid characters
    return sanitized_name

def buildOWL(input_dict, guideline_title, debug = False):
    """
    Generates an OWL (Web Ontology Language) ontology based on a hierarchical input dictionary, a guideline title, and optional debugging input.
    
    Args:
        input_dict (dict): A dictionary where each key represents a concept with values structured as 
                           [concept_id (str), concept_label (str), synonyms (list of str)]. The dictionary 
                           provides a hierarchy of concepts to be represented in OWL.
        guideline_title (str): The title of the guideline, used as the name for the main class and ontology.
        debug (bool): Optional; if True, uses a predefined sample of `input_dict` to assist in debugging.
                      Defaults to False.
    
    Returns:
        None. Serializes the generated OWL ontology as a Turtle file named `head_ontology.ttl`.

    Functionality:
        - Creates an RDF graph with an ontology based on the provided guideline title.
        - Binds a custom namespace (`ex`) and declares the ontology and main classes.
        - If `debug` is True, replaces `input_dict` with a predefined sample dictionary.
        - Iterates through each concept in `input_dict`, determines its parent concept using breadth-first 
          search (BFS), and adds it to the ontology as an OWL class, linked hierarchically.
        - Times and reports the BFS search process duration, and then serializes the final RDF graph 
          in Turtle format.
    """
    
    if not has_required_keys(input_dict):
        print("Your input dictionary does not have all the correct keys, make sure it has the following keys:")
        print("'lichaamsdelen', 'symptomen', 'diagnoses' en 'behandelingen'")
    conc = sanitize_uri(guideline_title)
    ex = Namespace(f"http://example.org/{conc}#")
    g = Graph()
    # Ontology Declaration
    g.bind("ex", ex)  # Bind the custom namespace for easier access
    g.add((URIRef(f"http://example.org/{conc}"), RDF.type, OWL.Ontology))

    main_class_name = sanitize_uri(guideline_title)
    main_class = URIRef(ex[main_class_name])
    patient_class_name = 'Patient'
    patient_class = URIRef(ex['123037004'])
    g.add((main_class, RDF.type, OWL.Class))
    g.add((main_class, RDFS.label, Literal(guideline_title)))
    g.add((patient_class, RDF.type, OWL.Class))
    g.add((patient_class, RDFS.label, Literal(patient_class_name)))


    if not debug:
        input_dict = identify_root_IDs(input_dict)
    else:
        input_dict = {'ear': ['117590005', 'Ear structure (body structure)', ['ear', 'ear structure']],
                      'head': ['69536005', 'Head structure (body structure)', ['head', 'head structure']],
                      'eardrum': ['42859004', "Tympanic membrane structure (body structure)", ['eardrum', 'tympanic membrane structure', 'tympanic membrane']]}
        
    all_keys = list(input_dict['lichaamsdelen'].keys())
    
    start = time.time()
    for classes, el in input_dict.items():
        if classes == 'lichaamsdelen':
            for key, items in el.items():
                other_keys = [k for k in all_keys if k != key]
                search_terms = other_keys

                #TODO: search term is alles behalve het element nu
                parent = BFS_ontology([],(items[0], items[1]), search_term = search_terms)
                if not(parent == 'patient'):
                    parent_id = input_dict['lichaamsdelen'][parent][0]
                else:
                    parent_id = '123037004'
                g = add_OWL_class(items, g, ex, parent_id)
        elif classes == 'symptomen':
            for key, items in el.items():
                parent_id= getFindings(items)
                g = add_OWL_class(items, g, ex, parent_id)
                g = add_OWL_relation(items, parent_id, g, ex, "has Finding Site", 123037004)

    end = time.time()
    print("BFS_ontology took", end - start, "seconds")
    g.serialize(destination='head_ontology.ttl', format='turtle')

def getFindings(items):
    parent = None
    if items[0] is not None:
        parent = queryFindingsFindingsiteById(items[0])
    return parent

def most_common(lst):
    counts = {item: lst.count(item) for item in set(lst)}
    max_count = max(counts.values())
    if max_count > 1:
        return max(counts, key=counts.get)
    else:
        return lst[0]

def identify_root_IDs(input_dict: dict):
    start = time.time()
    # We loop through the synonyms, gather all IDs and check the one that is most occuring
    if version == 'db':
        for key, value in input_dict.items():
            if key == 'lichaamsdelen':
                for key2, value2 in value.items():
                    print(key2) 
                    try:
                        value2 = init_most_cmmn_id(key2, value2, getSnomedConceptId)
                    except Exception as e:
                        print(value2[0])
                        print(f"While looking for word {key2} an error occured: {e}")
                    print(f"Keyword '{key2}' coupled to id {value2[0]}")
            elif key == 'symptomen':
                for key2, value2 in value.items():
                    print(key2)
                    #try:
                    value2 = init_most_cmmn_id(key2, value2, getSnomedFindingId)
                    #except Exception as e:
                        # print(value2[0])
                        # print(f"While looking for finding {key2} an error occured: {e}")
                    print(f"Keyword '{key2}' coupled to id {value2[0]}")
    else:
        for key, value in input_dict.items():
            ID_set = []
            ID_set.append(getSnomedConceptId(key))
            for synonym in value[2]:
                ID_set.append(getSnomedConceptId(synonym))
            value[0] = most_common(ID_set)
            value[1] = getConceptById(value[0])
            print(f"Keyword '{key}' coupled to id {value[0]}")
    end = time.time()
    print("identyfy_root_IDs took", end - start, "seconds")
    return input_dict

def has_required_keys(data_dict):
    required_keys = {'lichaamsdelen', 'symptomen', 'diagnoses', 'behandelingen'}
    return required_keys.issubset(data_dict.keys())

def init_most_cmmn_id(key2, value2, function):
    ID_set = []
    ID_key = function(key2)
    if ID_key != None:
        ID_set.append(function(key2)) 
    for synonym in value2[2]:
        ID = function(synonym) 
        if ID is not None:
            ID_set.append(ID)
    
    if len(ID_set) > 0:
        value2[0] = most_common(ID_set)
    else:
        print("Could not find any ID for value2, solution is needed")
        return value2
    value2[1] = queryConceptById(value2[0])
    
    return value2


dutchdictionary = {
    'oor':['ID', "prefered label", ['oor', 'structuur van oor']],
    'hoofd': ['ID', "prefered label",['hoofd', 'structuur van hoofd']], 
    #'External Auditory Canal': ['ID', "prefered label",['External Auditory Canal']],
    'trommelvlies': ['ID', "prefered label",['trommelvlies', 'membrana tympanica']]
}

englishdictionary = {
    'ear':['ID', "prefered label", ['ear', 'ear structure']],
    'head': ['ID', "prefered label",['head', 'head structure']], 
    #'External Auditory Canal': ['ID', "prefered label",['External Auditory Canal']],
    'eardrum': ['ID', "prefered label",['eardrum', 'tympanic membrane']]
}

input_dictionary = {
    'lichaamsdelen': {'oor': [None, None, ['gehoorgang', 'trommelvlies', 'oorschelp']], 
                    'gehoorgang': [None, None, ['auris externus']], \
                    'trommelvlies': [None, None, ['membrana tympani', 'tympanum']], 
                    'oorschelp': [None, None, ['pinna']]
                    },
    'symptomen' : {'oorpijn': [None, None, ['auralgia', 'pijn in het oor']], 
                   'jeuk in het oor': [None, None, ['pruritus auris']], 
                   'vocht uit het oor': [None, None, ['otorroe']], 
                   'gehoorverlies': [None, None, ['auditory loss']], 
                   'zwelling': [None, None, ['oedeem']], 
                   'roodheid': [None, None, ['erytheem']], 
                   'schilfering': [None, None, ['desquamatie']], 
                   'pijn bij tractie aan de oorschelp': [None, None, ['pijn bij trekken aan het oor']]
                    },
    'diagnoses': {'otitis externa': [None, None, ['uitwendige oorontsteking']], 
                  'otitis media acuta': [None, None, ['acute middenoorontsteking']], 
                  'furunkel': [None, None, ['boil']], 
                  'herpes zoster oticus': [None, None, ['zoster oticus']], 
                  'erysipelas': [None, None, ['rozevonk']], 
                  'corpus alienum': [None, None, ['vreemd voorwerp']], 
                  'cholesteatoom': [None, None, ['cholesteatoma']], 
                  'gehoorgangcarcinoom': [None, None, ['oor carcinoom']]},
    'behandelingen': {'zure oordruppels': [None, None, ['acida oordruppels']], 'hydrocortison': [None, None, ['hydrocortisone']], 'triamcinolonacetonide': [None, None, ['triamcinolone acetonide']], 'flucloxacilline': [None, None, ['flucloxacillin']], 'occlusietherapie': [None, None, ['tamponneren']], 'uitspuiten van de gehoorgang': [None, None, ['cleaning of the ear canal']]}
}


if version == 'db':
    #dictionary = dutchdictionary
    dictionary = input_dictionary
else:
    dictionary = englishdictionary

start = time.time()
buildOWL(dictionary, "Otitis Externa")
end = time.time()
print("Took", end - start, "seconds")

#a: findings (symptomen)/disorders opzoeken in snomed - body parts die je nog niet hebt toevoegen\

#1: scrapen NHG 
#2: identificeren van concepten (chatGPT) - 'dictionary' maken
#3: ID identificeren (API call?) + dubbele verwijderen - voor alles ID toevoegen
#4: DFS of !BFS! op parents - keyword matching: omhoog totdat we vinden dat head een parent is
#5: relatie toekennen (isPartOf)
#6: repeat - ook voor diagnoses?
#7: patient relatie voor overblijven

#8: titel richtlijn richtlijn toevoegen en linken aan symptomen + patient
# visualize_owl(file_name = "head_ontology.ttl")


# Results with debug=false and dictionary having ear, head and eardrum, each with 2 synonyms
## DB version took about 38-40 seconds to finish, with identify_root_IDs taking about 38 seconds and BFS loop taking +- 0.01 seconds
## API version took about 35-40 seconds to finish, with identify_root_IDs taking 16-18 seconds and BFS loop taking 17-19 seconds