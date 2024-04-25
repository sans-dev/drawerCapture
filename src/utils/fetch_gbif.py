import requests
import json
from tqdm import tqdm

keys_to_delete = [
    "nubKey",
    "nameKey",
    "taxonID",
    "sourceTaxonKey",
    "kingdom",
    "phylum",
    "kingdomKey",
    "phylumKey",
    "classKey",
    "orderKey",
    "familyKey",
    "genusKey",
    "speciesKey",
    "datasetKey",
    "constituentKey",
    "parentKey",
    "authorship",
    "nameType",
    "rank",
    "origin",
    "taxonomicStatus",
    "nomenclaturalStatus",
    "remarks",
    "numDescendants",
    "lastCrawled",
    "lastInterpreted",
    "issues",
]

orders_response = requests.get('https://api.gbif.org/v1/species/216/children?limit=50').json()
orders_response = [order for order in orders_response['results'] if order['rank'] == "ORDER"]
orders_pbar = tqdm(orders_response, position=0, leave=True)

limit = 800

species = []
for order in orders_pbar:
    order_name = order['order']
    
    families_response = requests.get(f'https://api.gbif.org/v1/species/{order["key"]}/children?limit={limit}').json()
    families_response = [fam for fam in families_response['results'] if fam['rank'] == "FAMILY"]

    for family in families_response:
        family_name = family['scientificName']

        genera_response = requests.get(f'https://api.gbif.org/v1/species/{family["key"]}/children?limit={limit}').json()
        genera_response = [genus for genus in genera_response['results'] if genus['rank'] == "GENUS"]

        for genus in genera_response:
            genus_name = genus['genus']

            species_response = requests.get(f'https://api.gbif.org/v1/species/{genus["key"]}/children?limit={limit}').json()
            species_response = [spec for spec in species_response['results'] if spec['rank'] == "SPECIES"]
            orders_pbar.set_description(f"Fetching species for: {order_name}, {family['scientificName']}, {genus['genus']}...")

            for sp in species_response:
                for key in keys_to_delete:
                    try:
                        del sp[key]
                    except KeyError as e:
                        orders_pbar.set_description(f"Key '{e}' missing in species response results of {sp['scientificName']}")
                species.append(sp)

with open('resources/taxonomy/taxonomy.json', 'w') as f:
    json.dump(species, f, indent=4)

print("Taxonomy saved to taxonomy.json")
