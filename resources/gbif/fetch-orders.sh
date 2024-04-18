#!/bin/bash

echo "Requesting insect orders from GBIF..."
response=$(curl -sS -X 'GET' \
  'https://api.gbif.org/v1/species/216/children?limit=50' \
  -H 'accept: application/json' \
  -H 'Accept-Language: en')

echo "Filtering orders and IDs..."
declare -A orders

while read -r line; do
    key=$(echo "$line" | jq -r 'keys[]')
    order=$(echo "$line" | jq -r '.[]')
    orders["$key"]=$order
done < <(echo "$response" | jq -c '.results[] | select(.orderKey != null) | {(.orderKey | tostring): .order}')

# JSON-like structure
declare -A taxonomy

# Accessing the orders
for key in "${!orders[@]}"; do
    order_name=${orders[$key]}
    echo "Requesting families for order $order_name with key $key"
    families_response=$(curl -sS -X 'GET' \
      "https://api.gbif.org/v1/species/$key/children?limit=3" \
      -H 'accept: application/json' \
      -H 'Accept-Language: en')

    # Initialize an array to store families
    families=()

    # Extracting families with rank "FAMILY"
    while read -r family_line; do
        rank=$(echo "$family_line" | jq -r '.rank')
        if [ "$rank" == "FAMILY" ]; then
            family_name=$(echo "$family_line" | jq -r '.scientificName')
            family_key=$(echo "$family_line" | jq -r '.key')

            # Initialize an array to store genera
            genera=()

            # Requesting genera for the family
            genera_response=$(curl -sS -X 'GET' \
              "https://api.gbif.org/v1/species/${family_key}/children?limit=3" \
              -H 'accept: application/json' \
              -H 'Accept-Language: en')

            # Extracting genera
            while read -r genus_line; do
                genus_name=$(echo "$genus_line" | jq -r '.genus')
                genus_key=$(echo "$genus_line" | jq -r '.key')
                genera+=( "{\"genus_name\":\"$genus_name\",\"genus_key\":\"$genus_key\"}" )
            done < <(echo "$genera_response" | jq -c '.results[] | select(.rank == "GENUS") | {genus: .genus, key: .key}')

            # Add family along with its genera to families array
            families+=( "{\"family_name\":\"$family_name\",\"family_key\":\"$family_key\",\"genera\":[$(IFS=,; echo "${genera[*]}")]}" )
        fi
    done < <(echo "$families_response" | jq -c '.results[] | select(.rank == "FAMILY")')

    # Storing families in the taxonomy
    taxonomy["$order_name"]=$(jq -n --arg key "$key" --argjson families "$(IFS=,; echo "[${families[*]}]")" '{order_key: $key, families: $families}')
done

# Printing the taxonomy
echo "Taxonomy:"
echo "${taxonomy[@]}" | jq .
