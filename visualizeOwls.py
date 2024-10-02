import matplotlib.pyplot as plt
import networkx as nx
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL

def visualize_owl(file_name):
    # Create a new graph and define namespaces
    g = Graph()
    g.parse(file_name, format="turtle")
    ex = Namespace("http://example.org/ear#")
    xsd = Namespace("http://www.w3.org/2001/XMLSchema#")

    # Visualization
    G = nx.DiGraph()
    labels = {}

    # Add classes and properties to the graph
    for s, p, o in g:
        if p == RDF.type and (o == OWL.Class or o == OWL.DatatypeProperty or o == OWL.ObjectProperty):
            node_label = str(s.split('#')[-1])  
            G.add_node(str(s))  
            labels[str(s)] = node_label  # Store the label to use for visualization
        elif p == RDFS.subClassOf:
            G.add_edge(str(o), str(s), label='subClassOf')  # Note: direction is subclass -> superclass
        elif p in {ex.hasName, ex.hasAge, ex.hasOffspring}:
            G.add_edge(str(s), str(o), label=str(p.split('#')[-1]))


    pos = nx.spring_layout(G)
    nx.draw(G, pos, labels=labels, with_labels=True, node_color='lightblue', node_size=2000, font_size=10, font_weight='bold', arrows=True)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    plt.title("Ontology Visualization")
    plt.show()
