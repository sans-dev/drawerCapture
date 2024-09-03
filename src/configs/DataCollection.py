from pathlib import Path

SYNONYMES = {
    'Order' : Path('resources/taxonomy/order_synonymes.json'),
    'Family': Path('resources/taxonomy/family_synonymes.json'),
    'Genus': Path('resources/taxonomy/genus_synonymes.json'),
    'Species': Path('resources/taxonomy/species_synonymes.json')
}

TAXONOMY = {
    'prod' : Path('resources/taxonomy/taxonomy_prod.json'),
    'test' : Path('tests/data/taxonomy_test.json'),
}

GEO  = {
    'level-0': Path('resources/countries/administrative-level-0.csv')
}