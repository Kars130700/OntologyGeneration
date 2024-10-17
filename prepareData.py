import requests
from bs4 import BeautifulSoup
import ast
import regex as re
# URL to scrape
url = 'https://richtlijnen.nhg.org/standaarden/otitis-externa#samenvatting'

# Send a GET request to the webpage
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

def get_text_by_header(soup, header_tag):
    result = []
    headers = soup.find_all(header_tag)
    
    for header in headers:
        # Add the header text with formatting
        header_text = f"{header.text.strip()}\n{'-' * len(header.text.strip())}"
        result.append(header_text)
        
        # Find all the siblings after the current header
        for sibling in header.find_next_siblings():
            # Stop if we encounter another header of the same or higher level
            if sibling.name and sibling.name.startswith('h') and sibling.name <= header_tag:
                break
            # Stop when the word "Details" is encountered in the text
            if 'Details' in sibling.text:
                break
            # Append text content from the sibling element, if it's a paragraph or div
            if sibling.name in ['p', 'div', 'ul', 'ol']:  # Can extend to other tags if needed
                result.append(sibling.get_text(strip=True))
        
        result.append('')  # Add a blank line between sections
    
    # Join the result list into a single string and return it
    return '\n'.join(result)


# Print text under each h1, h2, and h3 header

#get_text_by_header(soup, 'h3')
text = get_text_by_header(soup, 'h3')
prompt_1 = """What are the relevant body parts for ontology creation that you find in this text? List them in a dictionary (python), with the following format: 

dictionary = {
    'key':[None, None, [synoniemen key]], 
}
key is the body part, and synoniemen of the key are in a list. Try to order the parts on how much they occur in the text. Make sure the included keys are body parts. 
"""
prompt_2= """" Maak een python dictionary van de relevante lichaamsdelen die je in de bovenstaande tekst vind. Formateer de lichaamsdelen zo:
dictionary = {
    'key':[None, None, [synoniemen key]], 
}
Waarin 'key' het lichaamsdeel is en [synoniemen key] een lijst van synoniemen van het lichaamsdeel is. Verzeker jezelf er van dat alle genoemde keys echt lichaamsdelen zijn, dus onderdelen van de menselijke anatomie."""
prompt_3= """
Maak python dictionaries  van de relevante lichaamsdelen, symptomen, diagnoses en behandelingen die je in de bovenstaande tekst vind. Formateer de dictionaries als volgt:  
waarin de dictionaries de volgende formattering hebben:

lichaamsdelen = {
    'key':[None, None, [synoniemen key]], 
}
Waarin 'key' het lichaamsdeel is en [synoniemen key] een lijst van synoniemen van het lichaamsdeel is. Uiteindelijk is het resultaat dus 4 dictionaries: één dict genaamd lichaamsdelen, één genaamd symptomen, één genaamd diagnoses en één genaamd behandelingen. Verzeker jezelf er van dat alle genoemde keys in de lichaamsdelen dictionary echt lichaamsdelen zijn, dus onderdelen van de menselijke anatomie
"""

import os
import openai


api_key = os.getenv('SP_CHATGPT_API_KEY')

from openai import OpenAI
client = OpenAI(
    api_key = os.getenv('SP_CHATGPT_API_KEY'),
)

# completion = client.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {
#             "role": "user",
#             "content": text + prompt_3
#         }
#     ]
# )

#print(completion.choices[0].message)
content="""Hieronder zijn de gevraagde Python dictionaries gemaakt op basis van de informatie in de tekst.\n\n
python\n# Dictionary van lichaamsdelen\nlichaamsdelen = {\n    'oor': [None, None, ['gehoorgang', 'trommelvlies', 'oorschelp']],\n    'gehoorgang': [None, None, ['auris externus']],\n    'trommelvlies': [None, None, ['membrana tympani', 'tympanum']],\n    'oorschelp': [None, None, ['pinna']],\n}\n\n# Dictionary van symptomen\nsymptomen = {\n    'oorpijn': [None, None, ['auralgia', 'pijn in het oor']],\n    'jeuk in het oor': [None, None, ['pruritus auris']],\n    'vocht uit het oor': [None, None, ['otorroe']],\n    'gehoorverlies': [None, None, ['auditory loss']],\n    'zwelling': [None, None, ['oedeem']],\n    'roodheid': [None, None, ['erytheem']],\n    'schilfering': [None, None, ['desquamatie']],\n    'pijn bij tractie aan de oorschelp': [None, None, ['pijn bij trekken aan het oor']],\n}\n\n# Dictionary van diagnoses\ndiagnoses = {\n    'otitis externa': [None, None, ['uitwendige oorontsteking']],\n    'otitis media acuta': [None, None, ['acute middenoorontsteking']],\n    'furunkel': [None, None, ['boil']],\n    'herpes zoster oticus': [None, None, ['zoster oticus']],\n    'erysipelas': [None, None, ['rozevonk']],\n    'corpus alienum': [None, None, ['vreemd voorwerp']],\n    'cholesteatoom': [None, None, ['cholesteatoma']],\n    'gehoorgangcarcinoom': [None, None, ['oor carcinoom']],\n}\n\n# Dictionary van behandelingen\nbehandelingen = {\n    'zure oordruppels': [None, None, ['acida oordruppels']],\n    'hydrocortison': [None, None, ['hydrocortisone']],\n    'triamcinolonacetonide': [None, None, ['triamcinolone acetonide']],\n    'flucloxacilline': [None, None, ['flucloxacillin']],\n    'occlusietherapie': [None, None, ['tamponneren']],\n    'uitspuiten van de gehoorgang': [None, None, ['cleaning of the ear canal']],\n}\n
\n\nDeze dictionaries bevatten lichaamsdelen, symptomen, diagnoses en behandelingen zoals genoemd in de tekst. Elk lichaamsdeel bevat eventuele synoniemen die relevant zijn voor dat specifieke deel."""


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
