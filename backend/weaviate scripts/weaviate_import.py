import requests
import json
import os

WEAVIATE_ENDPOINT = "http://localhost:8080/v1"
DUMP_DIR = "weaviate_dump"

def load_objects(class_name):
    with open(f"{DUMP_DIR}/{class_name}_dump.json", 'r') as f:
        return json.load(f)

def import_objects(class_name, objects):
    for obj in objects:
        response = requests.post(f"{WEAVIATE_ENDPOINT}/objects", json=obj, headers={'X-Class-Name': class_name})
        response.raise_for_status()

def main():
    for filename in os.listdir(DUMP_DIR):
        if filename.endswith("_dump.json"):
            class_name = filename.replace("_dump.json", "")
            print(f"Importing data for class: {class_name}")
            objects = load_objects(class_name)
            import_objects(class_name, objects)
            print(f"Imported {len(objects)} objects for class: {class_name}")

    print("Data import completed.")

if __name__ == "__main__":
    main()
