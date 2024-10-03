# OntologyGeneration

Software Production ontology generation from guidelines.

This project involves retrieving SNOMED concepts using the FHIR API and translating them into an OWL ontology.

## How to Use This Repository

### Step 1: Install Dependencies

First, make sure you have cloned this repository to your local machine. After navigating to the folder where the repository is located, install the necessary dependencies by running the following command:

```sh
pip install -r requirements.txt
```

### Step 2: 

Run the program from SNOMED.py. With the call ```buildOWL('term')```, you can build a new ontology. Change the depth parameter to specify the depth of the tree.
Use ```visualize_owl("file_name.ttl")``` to visualize the generated tree structure
