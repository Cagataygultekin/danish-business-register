import json

# Load data from a JSON file in the current directory
with open("cvr_raw_response.txt", "r") as file:
    data = json.load(file)

def list_attributes(data, indent=0, parent_key=""):
    """
    Recursively retrieves keys and their nested structure within a JSON-like dictionary.
    """
    attributes = []
    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            attributes.append(f"{' ' * indent}{full_key}")
            attributes.extend(list_attributes(value, indent + 4, full_key))
    elif isinstance(data, list):
        if data:
            attributes.extend(list_attributes(data[0], indent + 4, parent_key))
    return attributes

# Extracting attributes from the 'data' JSON response
source_data = data['hits']['hits'][0]['_source']
attributes = list_attributes(source_data)

# Write attributes to a text file
with open("attributes_list.txt", "w") as file:
    file.write("\n".join(attributes))

print("Attributes written to attributes_list.txt")
