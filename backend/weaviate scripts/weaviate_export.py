import requests
import json
import os

WEAVIATE_ENDPOINT = "http://localhost:8080/v1"
DUMP_DIR = "weaviate_dump"


def fetch_schema():
    response = requests.get(f"{WEAVIATE_ENDPOINT}/schema")
    response.raise_for_status()
    return response.json()


def fetch_objects(class_name):
    objects = []
    cursor = None

    while True:
        params = {'limit': 100}
        if cursor:
            params['cursor'] = cursor

        response = requests.get(f"{WEAVIATE_ENDPOINT}/objects", params=params, headers={'X-Class-Name': class_name})
        response.raise_for_status()
        data = response.json()

        objects.extend(data['objects'])
        cursor = data.get('pageInformation', {}).get('nextCursor')

        if not cursor:
            break

    return objects


def save_objects(class_name, objects):
    with open(f"{DUMP_DIR}/{class_name}_dump.json", 'w') as f:
        json.dump(objects, f, indent=2)


def main():
    os.makedirs(DUMP_DIR, exist_ok=True)

    schema = fetch_schema()
    class_names = [cls['class'] for cls in schema['classes']]

    for class_name in class_names:
        print(f"Exporting data for class: {class_name}")
        objects = fetch_objects(class_name)
        save_objects(class_name, objects)
        print(f"Saved {len(objects)} objects for class: {class_name}")

    print("Data export completed.")


if __name__ == "__main__":
    main()
