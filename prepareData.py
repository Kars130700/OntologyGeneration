import requests
from bs4 import BeautifulSoup

# URL to scrape
url = 'https://richtlijnen.nhg.org/standaarden/otitis-externa#samenvatting'

# Send a GET request to the webpage
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Function to get text under each header
def get_text_by_header(soup, header_tag):
    headers = soup.find_all(header_tag)
    for header in headers:
        print(f"{header.text.strip()}\n{'-' * len(header.text.strip())}")
        # Find all the siblings after the current header
        for sibling in header.find_next_siblings():
            # Stop if we encounter another header of the same or higher level
            if sibling.name and sibling.name.startswith('h') and sibling.name <= header_tag:
                break
            # Stop when the word "Details" is encountered in the text
            if 'Details' in sibling.text:
                break
            # Print text content from the sibling element, if it's a paragraph or div
            if sibling.name in ['p', 'div', 'ul', 'ol']:  # Can extend to other tags if needed
                print(sibling.get_text(strip=True))
        print()

# Print text under each h1, h2, and h3 header

#get_text_by_header(soup, 'h3')
#get_text_by_header(soup, 'h3')
prompt_1 = """What are the relevant body parts for ontology creation that you find in this text? List them in a dictionary (python), with the following format: 

dictionary = {
    'key':[None, None, [synoniemen key]], 
}
key is the body part, and synoniemen of the key are in a list. Try to order the parts on how much they occur in the text. Make sure the included keys are body parts. 
"""
prompt_2= """"Maak een python dictionary van de relevante lichaamsdelen die je in de bovenstaande tekst vind. Formateer de lichaamsdelen zo:
dictionary = {
    'key':[None, None, [synoniemen key]], 
}
Waarin 'key' het lichaamsdeel is en [synoniemen key] een lijst van synoniemen van het lichaamsdeel is. Verzeker jezelf er van dat alle genoemde keys echt lichaamsdelen zijn, dus onderdelen van de menselijke anatomie."""


import os
import openai


api_key = os.getenv('SP_CHATGPT_API_KEY')

for key in os.environ.keys():
    print(key)
from openai import OpenAI
client = OpenAI(
    api_key = os.getenv('SP_CHATGPT_API_KEY'),
)

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming."
        }
    ]
)

print(completion.choices[0].message)