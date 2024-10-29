import regex as re
import ast
content = "Hier is de verbeterde en gedetailleerde versie van de dictionaries, rekening houdend met de eerdere verzoeken voor synoniemen en specificiteit bij symptomen:\n\n```python\nlichaamsdelen = {\n    'oor': [None, None, ['gehoororgaan', 'oorholte', 'gehoorgang']],\n    'gehoorgang': [None, None, ['uitwendige gehoorgang']],\n    'trommelvlies': [None, None, ['timpanum', 'membrana tympani']],\n    'oorschelp': [None, None, ['auris', 'pinna']],\n}\n\nsymptomen = {\n    'oorpijn': [None, None, ['otalgie', 'pijn aan het oor', 'pijnlijk oor']],\n    'jeuk in het oor': [None, None, ['pruritus in het oor', 'jeukende gehoorgang']],\n    'vocht uit het oor': [None, None, ['otorroe', 'vochtige gehoorgang', 'uitvloed uit het oor']],\n    'gehoorverlies': [None, None, ['hypacusis', 'verminderd gehoor', 'slecht horen']],\n    'zwelling van de gehoorgang': [None, None, ['oedeem van de gehoorgang', 'gezwollen gehoorgang']],\n    'roodheid van de gehoorgang': [None, None, ['erytheem van de gehoorgang', 'gehoorgang roodheid']],\n    'schilfering van de gehoorgang': [None, None, ['desquamatie van de gehoorgang', 'schilfers in het oor']],\n}\n\ndiagnoses = {\n    'otitis externa': [None, None, ['externe oorontsteking']],\n    'otitis media acuta': [None, None, ['acute middenoorontsteking']],\n    'furuunkel': [None, None, ['haarzakjesontsteking', 'furunkulose']],\n    'herpes zoster oticus': [None, None, ['gordelroos van het oor']],\n    'erysipelas': [None, None, ['rozen', 'erysipeloid']],\n    'corpus alienum': [None, None, ['vreemd voorwerp in het oor']],\n    'cholesteatoom': [None, None, ['holte-oor']],\n    'gehoorgangcarcinoom': [None, None, ['gehoorgangtumor']],\n}\n\nbehandelingen = {\n    'zure oordruppels met hydrocortison': [None, None, ['hydrocortison-oordruppels']],\n    'zure oordruppels met triamcinolonacetonide': [None, None, ['triamcinolon-oordruppels']],\n    'aluminiumacetotartraat-oordruppels': [None, None, ['aalroodzuur-oordruppels']],\n    'orale flucloxacilline': [None, None, ['flucloxacilline']],\n    'paracetamol': [None, None, ['acetaminophen']],\n}\n```\n\nIn deze verbeterde versie van de dictionaries zijn de symptomen specifieker beschreven met betrekking tot waar de symptomen zich bevinden, en zijn de synoniemen uitgebreider gemaakt met verschillende samenstellingen die de betekenis behouden."

def extract_python_dictionaries(text):
    # Dictionary to store the extracted dictionaries
    extracted_dictionaries = {}

    # List of dictionary names to search for
    dict_names = ['lichaamsdelen', 'symptomen', 'diagnoses', 'behandelingen']
    
    # Iterate over each dictionary name and try to find the corresponding dictionary
    for dict_name in dict_names:
        # Regular expression to capture each dictionary inside the text
        dict_pattern = re.search(rf'{dict_name}\s*=\s*({{.*?}})', text, re.DOTALL)

        if dict_pattern:
            dict_string = dict_pattern.group(1)  # Extract the dictionary part
            try:
                # Use ast.literal_eval to safely evaluate the string as a Python dictionary
                extracted_dict = ast.literal_eval(dict_string)
                extracted_dictionaries[dict_name] = extracted_dict
            except (SyntaxError, ValueError) as e:
                print(f"Error while parsing dictionary '{dict_name}': {e}")
        else:
            print(f"No valid dictionary found for '{dict_name}'.")

    return extracted_dictionaries
dictionary = extract_python_dictionaries(content)

print("lichaamsdelen:", dictionary["lichaamsdelen"])
print()
print("symptomen", dictionary["symptomen"])
print()
print("diagnoses", dictionary["diagnoses"])
print()
print("behandelingen", dictionary["behandelingen"])
print()
print(dictionary)