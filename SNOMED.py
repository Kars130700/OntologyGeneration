# This script uses the Snowstorm SNOMED-CT API. A standardised FHIR API is also available.

# Note that we recommend running your own Snowstorm instance for heavy script use.
# See https://github.com/IHTSDO/snowstorm

from urllib.request import urlopen, Request
from urllib.parse import quote
import json
import matplotlib.pyplot as plt
import networkx as nx
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL
import regex as re
from visualizeOwls import visualize_owl
from helperFunctions import getChildrenById, getSnomedConceptId, getParentsById
# Note to self: maybe treat like a shortest route algorithm?

baseUrl = 'https://browser.ihtsdotools.org/snowstorm/snomed-ct'
edition = 'MAIN/SNOMEDCT-NL'
version = '2024-09-30'

# IMPORTANT! You must update this user agent to avoid having your IP banned for 24 hours.
# Replace with a contact email so that we can contact you if your script causes excessive load on the public server
# For example: user_agent = 'example@example.com'
user_agent = 'tienvoortheorie@gmail.com'



def buildOntology(root_concept: str, tree: list, depth: int, ex, g):
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
    conceptId = getSnomedConceptId(root_concept) 
    if not conceptId:
        print(f"Concept '{root_concept}' not found.")
        return
    if depth == 0:
        g.serialize(destination='head_ontology.ttl', format='turtle')
        print("OWL ontology created successfully!")
        return tree
    
    # Get the children of the current concept
    new_tree = getParentsById(conceptId=conceptId)
    if new_tree:
        # Add the new_tree to the main tree
        tree.extend(new_tree)
        
        # Recursively build for each child
        for index in range(len(new_tree)):
            g = add_OWL_class(new_tree[index], g, ex, root_concept)
            buildOntology(new_tree[index], tree, depth - 1, ex, g)

    return tree

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

def buildOWL(concept):
    conc = sanitize_uri(concept)
    ex = Namespace(f"http://example.org/{conc}#")
    g = Graph()
    # Ontology Declaration
    g.bind("ex", ex)  # Bind the custom namespace for easier access
    g.add((URIRef(f"http://example.org/{conc}"), RDF.type, OWL.Ontology))

    main_class_name = sanitize_uri(concept)
    main_class = URIRef(ex[main_class_name])
    g.add((main_class, RDF.type, OWL.Class))
    g.add((main_class, RDFS.label, Literal(concept)))
    print(buildOntology(concept, [], 3, ex, g))

dictionary = {
    'ear':['ear', 'ear structure'],
    'head': ['head', 'head structure'], 
    'External Auditory Canal': ['External Auditory Canal'],
    'Eardrum': ['eardrum']
}
buildOWL("ear")

#visualize_owl(file_name = "generalized_ontology.ttl")
#visualize_owl(file_name = "otitis_externa_ontology.ttl")
# visualize_owl(file_name = "generalized_ontology.ttl")
visualize_owl(file_name = "otitis_ontology.ttl")

