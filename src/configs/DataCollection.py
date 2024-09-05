from pathlib import Path

SYNONYMES = {
    'Species': Path('assets/taxon/species_synonymes.json')
}

TAXONOMY = {
    'prod' : Path('assets/taxon/taxonomy_prod.json'),
    'test' : Path('assets/taxon/taxonomy_test.json'),
}

GEO  = {
    'level-0': Path('assets/geo/administrative-level-0.csv'),
    'level-1': Path('assets/geo/administrative-level-1.csv')
}