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
timeout = 5
try:
    orders_response = requests.get('https://api.gbif.org/v1/species/216/children?limit=50', timeout=timeout)
    orders_response.raise_for_status()
    orders_response = orders_response.json()
    orders_response = [order for order in orders_response['results'] if order['rank'] == "ORDER"]
    orders_pbar = tqdm(orders_response, position=0, leave=True)
except requests.exceptions.HTTPError as errh:
    print(f"HTTP Error while fetching Orders") 
    print(errh.args[0])
except KeyError as e:
    print(e)
except Exception as e:
    print(e)

limit = 800
species = []

for order in orders_pbar:
    order_name = order['order']
    try:
        families_response = requests.get(f'https://api.gbif.org/v1/species/{order["key"]}/children?limit={limit}', timeout=timeout)
        families_response.raise_for_status()
        families_response = families_response.json()
        families_response = [fam for fam in families_response['results'] if fam['rank'] == "FAMILY"]
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error while fetching families of order '{order_name}") 
        print(errh.args[0])
        continue
    except KeyError as e:
        print(e)
        continue
    except Exception as e:
        print(e)
        continue
    for family in families_response:
        family_name = family['scientificName']
        try:
            genera_response = requests.get(f'https://api.gbif.org/v1/species/{family["key"]}/children?limit={limit}', timeout=timeout)
            genera_response.raise_for_status()
            genera_response = genera_response.json()
            genera_response = [genus for genus in genera_response['results'] if genus['rank'] == "GENUS"]
        except requests.exceptions.HTTPError as errh:
            print(f"HTTP Error while fetching genera of family '{family_name}") 
            print(errh.args[0])
            continue
        except KeyError as e:
            print(e)
            continue
        except Exception as e:
            print(e)
            continue
        for genus in genera_response:
            genus_name = genus['genus']
            orders_pbar.set_description(f"Fetching species for: {order_name}, {family['scientificName']}, {genus['genus']}...")
            try:
                species_response = requests.get(f'https://api.gbif.org/v1/species/{genus["key"]}/children?limit={limit}', timeout=timeout)
                species_response.raise_for_status()
                species_response = species_response.json()
                species_response = [spec for spec in species_response['results'] if spec['rank'] == "SPECIES"]
            except requests.exceptions.HTTPError as errh:
                print(f"HTTP Error while fetching species of genus '{genus_name}") 
                print(errh.args[0])
                continue
            except KeyError as e:
                print(e)
                continue
            except Exception as e:
                print(e)
                continue

            for sp in species_response:
                for key in keys_to_delete:
                    try:
                        del sp[key]
                    except KeyError as e:
                        orders_pbar.set_description(f"Key '{e}' missing in species response results of {sp['scientificName']}")
                species.append(sp)

with open('resources/taxonomy/taxonomy.json', 'w') as f:
    json.dump(species, f, indent=2)

print("Taxonomy saved to taxonomy.json")
