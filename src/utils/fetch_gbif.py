import requests
import json
from tqdm import tqdm

taxonomy = {}

orders_response = requests.get('https://api.gbif.org/v1/species/216/children?limit=50').json()
orders_response = [order for order in orders_response['results'] if order['rank'] == "ORDER"]
orders_pbar = tqdm(orders_response, position=0, leave=True)
limit = 400
for order in orders_pbar:
    order_name = order['order']
    orders_pbar.set_description(f"Fetching family information for order {order_name}")
    
    families_response = requests.get(f'https://api.gbif.org/v1/species/{order["key"]}/children?limit={limit}').json()
    families_response = [fam for fam in families_response['results'] if fam['rank'] == "FAMILY"]
    fam_pbar = tqdm(families_response, position=1, leave=True)
    families = {}

    for family in fam_pbar:
        family_name = family['scientificName']
        fam_pbar.set_description(f"Fetching genus information for family {family_name}")

        genera_response = requests.get(f'https://api.gbif.org/v1/species/{family["key"]}/children?limit={limit}').json()
        genera_response = [genus for genus in genera_response['results'] if genus['rank'] == "GENUS"]
        genera_pbar = tqdm(genera_response, position=2, leave=True)
        genera = {}

        for genus in genera_pbar:
            genus_name = genus['genus']

            genera_pbar.set_description(f"Fetching species information for genus {genus_name}")
            species_response = requests.get(f'https://api.gbif.org/v1/species/{genus["key"]}/children?limit={limit}').json()
            species_response = [spec for spec in species_response['results'] if spec['rank'] == "FAMILY"]
            spec_pbar = tqdm(species_response, position=3, leave=True)
            species = {}

            for sp in spec_pbar:
                genera_pbar.set_description(f"Saving species information ...")
                species_name = sp['species']
                species[species_name] = [species_name, genus_name, family_name, order_name]

            genera[genus_name] = species

    families[family_name] = genera

taxonomy[order_name] = families

with open('taxonomy.json', 'w') as f:
    json.dump(taxonomy, f)

print("Taxonomy saved to taxonomy.json")