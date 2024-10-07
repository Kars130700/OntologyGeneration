import matplotlib.pyplot as plt
import networkx as nx
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL



### Using WebVOWL is easier:
### https://service.tib.eu/webvowl/
def visualize_owl(file_name):
    # Create a new graph and define namespaces
    g = Graph()
    try:
        g.parse(file_name, format="turtle")
    except Exception as e:
        print("Error parsing OWL file:", e)
        return
    
    ex = Namespace("http://example.org/otitis_externa#")
    # Visualization
    G = nx.DiGraph()
    labels = {}

    print(g)
    # Add classes and properties to the graph
    for s, p, o in g:
        #print(p)
        # Add nodes for classes and properties
        if p == RDF.type and (o == OWL.Class or o == OWL.ObjectProperty):
            label = str(s.split('#')[-1])
            #print(node_label)
            if o == OWL.Class:
                G.add_node(str(s))  
                labels[str(s)] = label  # Store the label to use for visualization
            elif o == OWL.ObjectProperty:
                G.add_edge(str(s), str(o), label=label)

        # Add subclass relationships
        elif p == RDFS.subClassOf:
            if p == ex.isPartOf:
                print(p)
                print(s)
            G.add_edge(str(o), str(s), label='subClassOf')  # Note: direction is subclass -> superclass

        # Add other relationships, including isPartOf
        #TODO this doesnt work, because it does not enter the loop
        elif isinstance(p, URIRef) and p.startswith(ex):
            property_label = str(p.split('#')[-1])
            G.add_edge(str(s), str(o), label=property_label)

    # Generate the layout for visualization
    pos = nx.spring_layout(G)
    nx.draw(G, pos, labels=labels, with_labels=True, node_color='lightblue', node_size=2000, font_size=10, font_weight='bold', arrows=True)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    plt.title("Ontology Visualization")
    plt.show()
