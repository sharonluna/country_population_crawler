# Countries Population Crawler
import pandas as pd
import requests
from bs4 import BeautifulSoup
from os import path
import sys
import re

# Load Dictionary to get unique countries 
cat_geo = pd.read_csv('Catálogo de relación geográfica.csv')
unique_countries = [country.strip().lower() for country in cat_geo['País'].unique()]

# Auxiliary functions ########################################################################
def load(key: str, value: int, data_dict: dict):
    """Fucntion to create dictionary with population per country

    Args:
        key (str): name of the country
        value (int): population
        data_dict (dict): empty dictionary
    """
    data_dict[key] = value

def clean_country_name(country_text: str) -> str: 
    """Function to clean country names

    Args:
        country_text (str): country name 

    Returns:
        str: cleaned country name
    """

    country = country_text.split('\xa0')[0]
    country = re.sub(r'\[.*?\]|\d+', '', country).strip()
    country = country.replace('\u200b','')
    words = country.split()
    country_cleaned = ' '.join(dict.fromkeys(words))  # Preserve original order, remove duplicates
    
    return country_cleaned

def scrape_population():

    url = 'https://es.wikipedia.org/wiki/Anexo:Países_y_territorios_dependientes_por_densidad_de_población'


    try:
        response = requests.get(url)
        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')

            table = soup.find('table', {'class': 'wikitable'})

            if table:
                population_data = {}

                # Iterate table rows
                for row in table.find_all('tr')[1:]:
                    columns = row.find_all('td')

                    if len(columns) >= 3:
                        # Get and clean country name
                        country = columns[1].text.strip().lower()
                        country = clean_country_name(country) 

                        population_text = columns[3].text.strip().replace('.', '').replace(',', '').replace('\xa0','')
                        # Convert population to integer
                        try:
                            population = int(population_text)
                        except ValueError:
                            population = None

                        # Search for countries included in file
                        if any(search_country == country for search_country in unique_countries):
                           load(country.title(), population, population_data)

                # Convert dictionary to DataFrame
                df_population = pd.DataFrame(list(population_data.items()), columns=['País', 'Población'])
                return df_population

            else:
                print("No table found on the Wikipedia page.")

        else:
            print(f"Error: Received bad response from {url} with status code {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")


# Call the Crawler
df_population = scrape_population()
if df_population is not None:
    print(df_population)

    # Save Df as csv
    df_population.to_csv('country_population.csv', index=False)

# Validate that all the countries that must be are included.
print(unique_countries)